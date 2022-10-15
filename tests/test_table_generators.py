import unittest

from table_generators import change_channel_keys

class TestChangeChannelKeys(unittest.TestCase):
    
    def test_change_channel_keys(self):
        data = [
            {
                "title": "Go готовить",
                "subscribers_count": "15K",
                "videos_count": "35",
                "total_views": "30K",
                "average_views_by_video": "12K",
                "channel_id": "458457"
            }
        ]
        new_data = change_channel_keys(data)

        self.assertTrue("Title" in new_data[0])
        self.assertTrue("# subs" in new_data[0])
        self.assertTrue("# videos" in new_data[0])
        self.assertTrue("# views" in new_data[0])
        self.assertTrue("Avg views" in new_data[0])
        self.assertTrue("id" in new_data[0])
    
if __name__ == '__main__':
    unittest.main()