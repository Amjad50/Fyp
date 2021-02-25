import unittest

from PIL import Image

from .symbol_segmenter import segment_image_crops


class SegmenterTestCase(unittest.TestCase):
    def test_multi_part_symbols(self):
        """
        This tests the segmentation of `=`, `:`, `i`, `j` characters with some extra characters as well
        """
        multi_part_symbols_img = Image.open('./testing_dataset/multi_part_symbols.png')
        image_segments = segment_image_crops(multi_part_symbols_img)

        self.assertEqual(len(image_segments), 7)
        self.assertListEqual(image_segments,
                             [(190, 93, 225, 96), (193, 113, 221, 159), (196, 19, 219, 65), (93, 87, 139, 103),
                              (149, 82, 156, 112), (16, 66, 34, 113), (37, 66, 65, 126)])

    def test_dot_on_frac(self):
        """
        This tests the segmentation of a dot character `.` on top of a `-` character which can happen
        when dealing with `1.5/x` for example.

        The reason for this test is because I thought this will fool the `i`,`j` simple identifier and would
        make it think that this is a valid `i` or `j` character, but it is identifying it correctly.
        """
        dot_on_frac_img = Image.open('./testing_dataset/dot_on_frac.png')
        image_segments = segment_image_crops(dot_on_frac_img)

        self.assertEqual(len(image_segments), 11)
        self.assertListEqual(image_segments,
                             [(22, 93, 227, 96), (52, 19, 75, 65), (86, 58, 93, 65), (102, 19, 130, 65),
                              (137, 19, 166, 67), (144, 113, 167, 159), (171, 18, 202, 65), (179, 152, 186, 159),
                              (195, 113, 223, 161), (69, 134, 115, 150), (24, 113, 42, 160)])


if __name__ == '__main__':
    unittest.main()
