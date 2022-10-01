import unittest

from change_filter import load_filters, change_filter_property, clear_filters

class TestChangeFilter(unittest.TestCase):
    
    def test_change_num_subscribers_prop(self):
        num_subscribers_lower_limit = 1000
        num_subscribers_upper_limit = "no_upper_limit"

        change_filter_property("test", "subscribers_count", num_subscribers_lower_limit, num_subscribers_upper_limit)

        filters = load_filters("test")
        self.assertEqual(filters["subscribers_count"][0], num_subscribers_lower_limit)
        self.assertEqual(filters["subscribers_count"][1], num_subscribers_upper_limit)
    
    def test_change_num_videos_prop(self):
        num_videos_lower_limit = 2
        num_videos_upper_limit = 5

        change_filter_property("test", "videos_count", num_videos_lower_limit, num_videos_upper_limit)

        filters = load_filters("test")
        self.assertEqual(filters["videos_count"][0], num_videos_lower_limit)
        self.assertEqual(filters["videos_count"][1], num_videos_upper_limit)
    
    def test_change_total_views_prop(self):
        total_views_lower_limit = 15_000
        total_views_upper_limit = 10_000_000

        change_filter_property("test", "total_views", total_views_lower_limit, total_views_upper_limit)

        filters = load_filters("test")
        self.assertEqual(filters["total_views"][0], total_views_lower_limit)
        self.assertEqual(filters["total_views"][1], total_views_upper_limit)
    
    def test_change_avg_views_by_video_prop(self):
        avg_views_by_video_lower_limit = 10_000
        avg_views_by_video_upper_limit = "no_upper_limit"

        change_filter_property("test", "average_views_by_video", avg_views_by_video_lower_limit, avg_views_by_video_upper_limit)

        filters = load_filters("test")
        self.assertEqual(filters["average_views_by_video"][0], avg_views_by_video_lower_limit)
        self.assertEqual(filters["average_views_by_video"][1], avg_views_by_video_upper_limit)
    
    def setUp(self):
        clear_filters("test")


if __name__ == '__main__':
    unittest.main()