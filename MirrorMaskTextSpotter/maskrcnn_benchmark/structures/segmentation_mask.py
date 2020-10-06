# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
import torch

import pycocotools.mask as mask_utils
import numpy as np
import cv2
from PIL import Image
from maskrcnn_benchmark.utils.chars import num2char, char2num
from shapely.geometry import Polygon
from shapely import affinity
# transpose
FLIP_LEFT_RIGHT = 0
FLIP_TOP_BOTTOM = 1


class Mask(object):
    """
    This class is unfinished and not meant for use yet
    It is supposed to contain the mask for an object as
    a 2d tensor
    """

    def __init__(self, masks, size, mode):
        self.masks = masks
        self.size = size
        self.mode = mode

    def transpose(self, method):
        if method not in (FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM):
            raise NotImplementedError(
                "Only FLIP_LEFT_RIGHT and FLIP_TOP_BOTTOM implemented"
            )

        width, height = self.size
        if method == FLIP_LEFT_RIGHT:
            dim = width
            idx = 2
        elif method == FLIP_TOP_BOTTOM:
            dim = height
            idx = 1

        flip_idx = list(range(dim)[::-1])
        flipped_masks = self.masks.index_select(dim, flip_idx)
        return Mask(flipped_masks, self.size, self.mode)

    def crop(self, box):
        w, h = box[2] - box[0], box[3] - box[1]

        cropped_masks = self.masks[:, box[1] : box[3], box[0] : box[2]]
        return Mask(cropped_masks, size=(w, h), mode=self.mode)

    def resize(self, size, *args, **kwargs):
        pass


class SegmentationMask(object):
    """
    This class stores the segmentations for all objects in the image
    """

    def __init__(self, polygons, size, mode=None):
        """
        Arguments:
            polygons: a list of list of lists of numbers. The first
                level of the list correspond to individual instances,
                the second level to all the polygons that compose the
                object, and the third level to the polygon coordinates.
        """
        assert isinstance(polygons, list)

        self.polygons = [Polygons(p, size, mode) for p in polygons]
        self.size = size
        self.mode = mode

    def transpose(self, method):
        if method not in (FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM):
            raise NotImplementedError(
                "Only FLIP_LEFT_RIGHT and FLIP_TOP_BOTTOM implemented"
            )

        flipped = []
        for polygon in self.polygons:
            flipped.append(polygon.transpose(method))
        return SegmentationMask(flipped, size=self.size, mode=self.mode)

    def crop(self, box,keep_ind=None):
        w, h = box[2] - box[0], box[3] - box[1]
        if keep_ind is not None:
            self.polygons=np.array(self.polygons)
            self.polygons = self.polygons[keep_ind]
        cropped = []
        for polygon in self.polygons:
            cropped.append(polygon.crop(box))
        return SegmentationMask(cropped, size=(w, h), mode=self.mode)

    def rotate(self, angle, r_c, start_h, start_w):
        rotated=[]
        for polygon in self.polygons:
            rotated.append(polygon.rotate(angle,r_c,start_h,start_w))
        return SegmentationMask(rotated,size=(r_c[0]*2,r_c[1]*2),mode=self.mode)

    def resize(self, size, *args, **kwargs):
        scaled = []
        for polygon in self.polygons:
            scaled.append(polygon.resize(size, *args, **kwargs))
        return SegmentationMask(scaled, size=size, mode=self.mode)

    def to(self, *args, **kwargs):
        return self

    def __getitem__(self, item):
        if isinstance(item, (int, slice)):
            selected_polygons = [self.polygons[item]]
        else:
            # advanced indexing on a single dimension
            selected_polygons = []
            if isinstance(item, torch.Tensor) and item.dtype == torch.uint8:
                item = item.nonzero()
                item = item.squeeze(1) if item.numel() > 0 else item
                item = item.tolist()
            for i in item:
                selected_polygons.append(self.polygons[i])
        return SegmentationMask(selected_polygons, size=self.size, mode=self.mode)

    def __iter__(self):
        return iter(self.polygons)

    def __repr__(self):
        s = self.__class__.__name__ + "("
        s += "num_instances={}, ".format(len(self.polygons))
        s += "image_width={}, ".format(self.size[0])
        s += "image_height={})".format(self.size[1])
        return s


class Polygons(object):
    """
    This class holds a set of polygons that represents a single instance
    of an object mask. The object can be represented as a set of
    polygons
    """

    def __init__(self, polygons, size, mode):
        # assert isinstance(polygons, list), '{}'.format(polygons)
        if isinstance(polygons, list):
            polygons = [torch.as_tensor(p, dtype=torch.float32) for p in polygons]
        elif isinstance(polygons, Polygons):
            polygons = polygons.polygons

        self.polygons = polygons
        self.size = size
        self.mode = mode

    def transpose(self, method):
        if method not in (FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM):
            raise NotImplementedError(
                "Only FLIP_LEFT_RIGHT and FLIP_TOP_BOTTOM implemented"
            )

        flipped_polygons = []
        width, height = self.size
        if method == FLIP_LEFT_RIGHT:
            dim = width
            idx = 0
        elif method == FLIP_TOP_BOTTOM:
            dim = height
            idx = 1

        for poly in self.polygons:
            p = poly.clone()
            TO_REMOVE = 1
            p[idx::2] = dim - poly[idx::2] - TO_REMOVE
            flipped_polygons.append(p)

        return Polygons(flipped_polygons, size=self.size, mode=self.mode)

    def rotate(self, angle, r_c, start_h, start_w):
        poly=self.polygons[0].numpy().reshape(-1,2)
        poly[:, 0]+=start_w
        poly[:, 1]+=start_h
        polys=Polygon(poly)
        r_polys=list(affinity.rotate(polys,angle,r_c).boundary.coords[:-1])
        p=[]
        for r in r_polys:
            p+=list(r)
        return Polygons([p], size=self.size, mode=self.mode)

    def crop(self, box):
        w, h = box[2] - box[0], box[3] - box[1]

        # TODO chck if necessary
        w = max(w, 1)
        h = max(h, 1)

        cropped_polygons = []

        for poly in self.polygons:
            p = poly.clone()
            p[0::2] = p[0::2] - box[0]  # .clamp(min=0, max=w)
            p[1::2] = p[1::2] - box[1]  # .clamp(min=0, max=h)
            cropped_polygons.append(p)

        return Polygons(cropped_polygons, size=(w, h), mode=self.mode)

    def resize(self, size, *args, **kwargs):
        ratios = tuple(float(s) / float(s_orig) for s, s_orig in zip(size, self.size))
        if ratios[0] == ratios[1]:
            ratio = ratios[0]
            scaled_polys = [p * ratio for p in self.polygons]
            return Polygons(scaled_polys, size, mode=self.mode)

        ratio_w, ratio_h = ratios
        scaled_polygons = []
        for poly in self.polygons:
            p = poly.clone()
            p[0::2] *= ratio_w
            p[1::2] *= ratio_h
            scaled_polygons.append(p)

        return Polygons(scaled_polygons, size=size, mode=self.mode)

    def convert(self, mode):
        width, height = self.size
        if mode == "mask":
            rles = mask_utils.frPyObjects(
                [p.numpy() for p in self.polygons], height, width
            )
            rle = mask_utils.merge(rles)
            mask = mask_utils.decode(rle)
            mask = torch.from_numpy(mask)
            # TODO add squeeze?
            return mask

    def __repr__(self):
        s = self.__class__.__name__ + "("
        s += "num_polygons={}, ".format(len(self.polygons))
        s += "image_width={}, ".format(self.size[0])
        s += "image_height={}, ".format(self.size[1])
        s += "mode={})".format(self.mode)
        return s


class CharPolygons(object):
    """
    This class holds a set of polygons that represents a single instance
    of an object mask. The object can be represented as a set of
    polygons
    """

    def __init__(self, char_boxes, word=None, use_char_ann=False, char_classes=None, size=None, mode=None):
        if isinstance(char_boxes, CharPolygons):
            if char_classes is None:
                char_classes = char_boxes.char_classes
            self.word = char_boxes.word
            char_boxes = char_boxes.char_boxes
        else:
            if char_classes is None:
                char_classes = [torch.as_tensor(p[8], dtype=torch.float32) for p in char_boxes]
            char_boxes = [torch.as_tensor(p[:8], dtype=torch.float32) for p in char_boxes]   
            self.word = word  
        self.char_boxes = char_boxes
        self.char_classes = char_classes
        self.size = size
        self.mode = mode
        self.use_char_ann = use_char_ann

    def transpose(self, method):
        if method not in (FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM):
            raise NotImplementedError(
                "Only FLIP_LEFT_RIGHT and FLIP_TOP_BOTTOM implemented"
            )

        flipped_polygons = []
        width, height = self.size
        if method == FLIP_LEFT_RIGHT:
            dim = width
            idx = 0
        elif method == FLIP_TOP_BOTTOM:
            dim = height
            idx = 1

        for char_box in self.char_boxes:
            p = char_box.clone()
            TO_REMOVE = 1
            p[idx::2] = dim - char_box[idx::2] - TO_REMOVE
            flipped_polygons.append(p)

        return CharPolygons(flipped_polygons, word=self.word, use_char_ann=self.use_char_ann, char_classes=self.char_classes, size=self.size, mode=self.mode)

    def crop(self, box):
        w, h = box[2] - box[0], box[3] - box[1]

        # TODO chck if necessary
        w = max(w, 1)
        h = max(h, 1)
        cropped_polygons = []
        for char_box in self.char_boxes:
            p = char_box.clone()
            p[0::2] = p[0::2] - box[0]  # .clamp(min=0, max=w)
            p[1::2] = p[1::2] - box[1]  # .clamp(min=0, max=h)
            cropped_polygons.append(p)

        return CharPolygons(cropped_polygons, word=self.word, use_char_ann=self.use_char_ann, char_classes=self.char_classes, size=(w, h), mode=self.mode)

    def rotate(self, angle, r_c, start_h, start_w):
        r_polys = []
        for poly in self.char_boxes:
            poly = poly.numpy()
            poly[0::2] += start_w
            poly[1::2] += start_h
            poly= Polygon(np.array(poly).reshape(4,2))
            r_poly = np.array(list(affinity.rotate(poly, angle, r_c).boundary.coords[:-1])).reshape(-1, 8)
            r_polys.append(r_poly[0])
        return CharPolygons(r_polys, word=self.word, use_char_ann=self.use_char_ann,char_classes=self.char_classes,size=(r_c[0]*2,r_c[1]*2), mode=self.mode)

    def resize(self, size, *args, **kwargs):
        ratios = tuple(float(s) / float(s_orig) for s, s_orig in zip(size, self.size))
        if ratios[0] == ratios[1]:
            ratio = ratios[0]
            scaled_polys = [p * ratio for p in self.char_boxes]
            return CharPolygons(scaled_polys, word=self.word, use_char_ann=self.use_char_ann, char_classes=self.char_classes, size=size, mode=self.mode)

        ratio_w, ratio_h = ratios
        scaled_polygons = []
        for poly in self.char_boxes:
            p = poly.clone()
            p[0::2] *= ratio_w
            p[1::2] *= ratio_h
            scaled_polygons.append(p)

        return CharPolygons(scaled_polygons, word=self.word, use_char_ann=self.use_char_ann, char_classes=self.char_classes, size=size, mode=self.mode)

    def convert(self, mode):
        width, height = self.size
        if mode == "char_mask":
            if not self.use_char_ann:
                char_map = -np.ones((height, width))
                char_map_weight = np.zeros((37,))
            else:
                char_map = np.zeros((height, width))
                char_map_weight = np.ones((37,))
                for i, p in enumerate(self.char_boxes):
                    poly=p.numpy().reshape(4,2)
                    # x_center = np.mean(poly[:,0], axis = 0).astype(np.int32)
                    # y_center = np.mean(poly[:,1], axis = 0).astype(np.int32)
                    poly=shrink_poly(poly,0.25)
                    cv2.fillPoly(char_map,[poly.astype(np.int32)],int(self.char_classes[i]))
                    # if is_poly_inbox(poly, height, width) and x_center>=0 and x_center<width and y_center>=0 and y_center<height:
                    #     spoly=shrink_rect(poly,0.25)
                    #     spoly = spoly.astype(np.int32)
                    #     sbox_xmin_shrink = max(0, min(spoly[:,0]))
                    #     sbox_xmax_shrink = min(width - 1, max(spoly[:,0]))
                    #     sbox_ymin_shrink = max(0, min(spoly[:,1]))
                    #     sbox_ymax_shrink = min(height - 1, max(spoly[:,1]))
                    #     ## very small char box
                    #     if sbox_xmax_shrink == sbox_xmin_shrink:
                    #         sbox_xmax_shrink = sbox_xmin_shrink + 1
                    #     if sbox_ymax_shrink == sbox_ymin_shrink:
                    #         sbox_ymax_shrink = sbox_ymin_shrink + 1
                    #     char_map[sbox_ymin_shrink:sbox_ymax_shrink, sbox_xmin_shrink:sbox_xmax_shrink] = int(self.char_classes[i])
                pos_index = np.where(char_map > 0)
                pos_num = pos_index[0].size
                if pos_num > 0:
                    pos_weight = 1.0 * (height*width - pos_num)/pos_num
                    char_map_weight[1:] = pos_weight
            return torch.from_numpy(char_map), torch.from_numpy(char_map_weight)
        elif mode == "seq_char_mask":
            decoder_target = (38 - 1) * np.ones((32, ))
            word_target = -np.ones((32, ))
            if not self.use_char_ann:
                char_map = -np.ones((height, width))
                char_map_weight = np.zeros((37,))
                for i, char in enumerate(self.word):
                    if i > 31:
                        break
                    decoder_target[i] = char2num(char)
                    word_target[i] = char2num(char)
                end_point = min(max(1, len(self.word)), 31)
                word_target[end_point] = 37
            else:
                char_map = np.zeros((height, width))
                char_map_weight = np.ones((37,))
                word_length = 0
                for i, p in enumerate(self.char_boxes):
                    poly=p.numpy().reshape(4,2)
                    # x_center = np.mean(poly[:,0], axis = 0).astype(np.int32)
                    # y_center = np.mean(poly[:,1], axis = 0).astype(np.int32)
                    # if is_poly_inbox(poly, height, width):
                    if i < 32:
                        decoder_target[i] = int(self.char_classes[i])
                        word_target[i] = int(self.char_classes[i])
                        word_length += 1
                    poly=shrink_poly(poly,0.25)
                    cv2.fillPoly(char_map,[poly.astype(np.int32)],int(self.char_classes[i]))
                        # if x_center>=0 and x_center<width and y_center>=0 and y_center<height:
                        #     spoly=shrink_rect(poly,0.25)
                        #     spoly = spoly.astype(np.int32)
                        #     sbox_xmin_shrink = max(0, min(spoly[:,0]))
                        #     sbox_xmax_shrink = min(width - 1, max(spoly[:,0]))
                        #     sbox_ymin_shrink = max(0, min(spoly[:,1]))
                        #     sbox_ymax_shrink = min(height - 1, max(spoly[:,1]))
                        #     ## very small char box
                        #     if sbox_xmax_shrink == sbox_xmin_shrink:
                        #         sbox_xmax_shrink = sbox_xmin_shrink + 1
                        #     if sbox_ymax_shrink == sbox_ymin_shrink:
                        #         sbox_ymax_shrink = sbox_ymin_shrink + 1
                        #     char_map[sbox_ymin_shrink:sbox_ymax_shrink, sbox_xmin_shrink:sbox_xmax_shrink] = int(self.char_classes[i])
                end_point = min(max(1, word_length), 31)
                word_target[end_point] = 37
                pos_index = np.where(char_map > 0)
                pos_num = pos_index[0].size
                if pos_num > 0:
                    pos_weight = 1.0 * (height*width - pos_num)/pos_num
                    char_map_weight[1:] = pos_weight
            return torch.from_numpy(char_map), torch.from_numpy(char_map_weight), torch.from_numpy(decoder_target), torch.from_numpy(word_target)

    def creat_color_map(self, n_class, width):
        splits = int(np.ceil(np.power((n_class * 1.0), 1.0 / 3)))
        maps = []
        for i in range(splits):
            r = int(i * width * 1.0 / (splits-1))
            for j in range(splits):
                g = int(j * width * 1.0 / (splits-1))
                for k in range(splits-1):
                    b = int(k * width * 1.0 / (splits-1))
                    maps.append([r, g, b])
        return np.array(maps)

    def __repr__(self):
        s = self.__class__.__name__ + "("
        s += "num_char_boxes={}, ".format(len(self.char_boxes))
        s += "num_char_classes={}, ".format(len(self.char_classes))
        s += "image_width={}, ".format(self.size[0])
        s += "image_height={}, ".format(self.size[1])
        s += "mode={})".format(self.mode)
        return s


class SegmentationCharMask(object):
    def __init__(self, chars_boxes, words=None, use_char_ann=True, size=None, mode=None):
        # self.chars_boxes=[CharPolygons(char_boxes, word=word, use_char_ann=use_char_ann, size=size, mode=mode) for char_boxes, word in zip(chars_boxes, words)]
        if words is None:
            self.chars_boxes=[CharPolygons(char_boxes, word=None, use_char_ann=use_char_ann, size=size, mode=mode) for char_boxes in chars_boxes]
        else:
            self.chars_boxes=[CharPolygons(char_boxes, word=words[i], use_char_ann=use_char_ann, size=size, mode=mode) for i, char_boxes in enumerate(chars_boxes)]
        self.size=size
        self.mode=mode
        self.use_char_ann=use_char_ann

    def transpose(self, method):
        if method not in (FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM):
            raise NotImplementedError(
                "Only FLIP_LEFT_RIGHT and FLIP_TOP_BOTTOM implemented"
            )

        flipped = []
        for char_boxes in self.chars_boxes:
            flipped.append(char_boxes.transpose(method))
        return SegmentationCharMask(flipped, use_char_ann=self.use_char_ann, size=self.size, mode=self.mode)

    def crop(self, box,keep_ind):
        cropped=[]
        w, h = box[2] - box[0], box[3] - box[1]
        if keep_ind is not None:
            self.chars_boxes=np.array(self.chars_boxes)
            self.chars_boxes = self.chars_boxes[keep_ind]
        for char_boxes in self.chars_boxes:
            cropped.append(char_boxes.crop(box))
        return SegmentationCharMask(cropped, use_char_ann=self.use_char_ann, size=(w, h), mode=self.mode)

    def resize(self, size, *args, **kwargs):
        scaled = []
        for char_boxes in self.chars_boxes:
            scaled.append(char_boxes.resize(size, *args, **kwargs))
        return SegmentationCharMask(scaled, use_char_ann=self.use_char_ann, size=size, mode=self.mode)

    def rotate(self, angle, r_c, start_h, start_w):
        rotated=[]
        for char_boxes in self.chars_boxes:
            rotated.append(char_boxes.rotate(angle,r_c,start_h,start_w))
        return SegmentationCharMask(rotated,use_char_ann=self.use_char_ann, size=(r_c[0]*2,r_c[1]*2), mode=self.mode)

    def __iter__(self):
        return iter(self.chars_boxes)

    def __getitem__(self, item):
        if isinstance(item, (int, slice)):
            selected_chars_boxes = [self.chars_boxes[item]]
        else:
            # advanced indexing on a single dimension
            selected_chars_boxes = []
            if isinstance(item, torch.Tensor) and item.dtype == torch.uint8:
                item = item.nonzero()
                item = item.squeeze(1) if item.numel() > 0 else item
                item = item.tolist()
            for i in item:
                if i >= len(self.chars_boxes):
                    print(i)
                    print('chars_boxes.shape: ', len(self.chars_boxes))
                    input()
                selected_chars_boxes.append(self.chars_boxes[i])
        return SegmentationCharMask(selected_chars_boxes, use_char_ann=self.use_char_ann, size=self.size, mode=self.mode)

    def __repr__(self):
        s = self.__class__.__name__ + "("
        s += "num_char_boxes={}, ".format(len(self.chars_boxes))
        s += "image_width={}, ".format(self.size[0])
        s += "image_height={})".format(self.size[1])
        return s


def shrink_poly(poly, shrink):
    # shrink ratio
    R = shrink
    r = [None, None, None, None]
    for i in range(4):
        r[i] = min(np.linalg.norm(poly[i] - poly[(i + 1) % 4]),
                   np.linalg.norm(poly[i] - poly[(i - 1) % 4]))
    # find the longer pair
    if np.linalg.norm(poly[0] - poly[1]) + np.linalg.norm(poly[2] - poly[3]) > \
            np.linalg.norm(poly[0] - poly[3]) + np.linalg.norm(poly[1] - poly[2]):
        # first move (p0, p1), (p2, p3), then (p0, p3), (p1, p2)
        ## p0, p1
        theta = np.arctan2((poly[1][1] - poly[0][1]), (poly[1][0] - poly[0][0]))
        poly[0][0] += R * r[0] * np.cos(theta)
        poly[0][1] += R * r[0] * np.sin(theta)
        poly[1][0] -= R * r[1] * np.cos(theta)
        poly[1][1] -= R * r[1] * np.sin(theta)
        ## p2, p3
        theta = np.arctan2((poly[2][1] - poly[3][1]), (poly[2][0] - poly[3][0]))
        poly[3][0] += R * r[3] * np.cos(theta)
        poly[3][1] += R * r[3] * np.sin(theta)
        poly[2][0] -= R * r[2] * np.cos(theta)
        poly[2][1] -= R * r[2] * np.sin(theta)
        ## p0, p3
        theta = np.arctan2((poly[3][0] - poly[0][0]), (poly[3][1] - poly[0][1]))
        poly[0][0] += R * r[0] * np.sin(theta)
        poly[0][1] += R * r[0] * np.cos(theta)
        poly[3][0] -= R * r[3] * np.sin(theta)
        poly[3][1] -= R * r[3] * np.cos(theta)
        ## p1, p2
        theta = np.arctan2((poly[2][0] - poly[1][0]), (poly[2][1] - poly[1][1]))
        poly[1][0] += R * r[1] * np.sin(theta)
        poly[1][1] += R * r[1] * np.cos(theta)
        poly[2][0] -= R * r[2] * np.sin(theta)
        poly[2][1] -= R * r[2] * np.cos(theta)
    else:
        ## p0, p3
        # print poly
        theta = np.arctan2((poly[3][0] - poly[0][0]), (poly[3][1] - poly[0][1]))
        poly[0][0] += R * r[0] * np.sin(theta)
        poly[0][1] += R * r[0] * np.cos(theta)
        poly[3][0] -= R * r[3] * np.sin(theta)
        poly[3][1] -= R * r[3] * np.cos(theta)
        ## p1, p2
        theta = np.arctan2((poly[2][0] - poly[1][0]), (poly[2][1] - poly[1][1]))
        poly[1][0] += R * r[1] * np.sin(theta)
        poly[1][1] += R * r[1] * np.cos(theta)
        poly[2][0] -= R * r[2] * np.sin(theta)
        poly[2][1] -= R * r[2] * np.cos(theta)
        ## p0, p1
        theta = np.arctan2((poly[1][1] - poly[0][1]), (poly[1][0] - poly[0][0]))
        poly[0][0] += R * r[0] * np.cos(theta)
        poly[0][1] += R * r[0] * np.sin(theta)
        poly[1][0] -= R * r[1] * np.cos(theta)
        poly[1][1] -= R * r[1] * np.sin(theta)
        ## p2, p3
        theta = np.arctan2((poly[2][1] - poly[3][1]), (poly[2][0] - poly[3][0]))
        poly[3][0] += R * r[3] * np.cos(theta)
        poly[3][1] += R * r[3] * np.sin(theta)
        poly[2][0] -= R * r[2] * np.cos(theta)
        poly[2][1] -= R * r[2] * np.sin(theta)
    return poly

def shrink_rect(poly, shrink):
    xmin = min(poly[:,0])
    xmax = max(poly[:,0])
    ymin = min(poly[:,1])
    ymax = max(poly[:,1])
    # assert xmax > xmin and ymax > ymin
    xc = (xmax + xmin) / 2
    yc = (ymax + ymin) / 2
    w = xmax - xmin
    h = ymax - ymin
    sxmin = xc - w/2*shrink
    sxmax = xc + w/2*shrink
    symin = yc - h/2*shrink
    symax = yc + h/2*shrink
    return np.array([sxmin, symin, sxmax, symin, sxmax, symax, sxmin, symax]).reshape((4, 2))

def is_poly_inbox(poly, height, width):
    min_x = min(poly[:, 0])
    min_y = min(poly[:, 1])
    max_x = max(poly[:, 0])
    max_y = max(poly[:, 1])
    if (max_x < 0 and max_y < 0) or (min_x > width and min_y > height):
        return False
    else:
        return True

