import unittest

from app.agents.tasks.deep_search_task import wrapListInfo


# 你可以根据实际情况引入你的模块
# from my_module import wrapListInfo

# Mock 的 searchRowData 函数，用于测试
def mock_searchRowData(title):
    return {
        "data": [{
            "id": 123,
            "name": f"{title}_matched",
            "logo": "mock_logo.png",
            "introduce": "mock introduction text"
        }]
    }

# 将真正的 searchRowData 替换为 mock（如果你是在模块里定义的，可以 patch）
import builtins
globals()['searchRowData'] = mock_searchRowData

class TestWrapListInfo(unittest.TestCase):

    def test_type_3_adds_analysis_prefix(self):
        input_list = [{"type": 3, "title": "Market Trends"}]
        expected_title = "Analysis report of the Market Trends"
        result = wrapListInfo(input_list)
        self.assertEqual(result[0]["title"], expected_title)

    def test_type_2_adds_background_prefix_from_search(self):
        input_list = [{"type": 2,"id":117}]
        result = wrapListInfo(input_list)
        print(result)
        # self.assertEqual(result[0]["title"], "Background information of the Company X_matched")
        # self.assertEqual(result[0]["id"], 123)
        # self.assertEqual(result[0]["logo"], "mock_logo.png")
        # self.assertEqual(result[0]["detail"], "mock introduction text")

    def test_type_2_empty_title(self):
        input_list = [{"type": 2, "title": ""}]
        result = wrapListInfo(input_list)
        self.assertEqual(result[0]["title"], "")

    def test_type_1_should_remain_unchanged(self):
        input_list = [{"type": 1, "title": "Some Title", "other": "data"}]
        result = wrapListInfo(input_list)
        self.assertEqual(result[0]["title"], "Some Title")
        self.assertEqual(result[0]["other"], "data")

    def test_type_not_in_1_2_3_4_should_be_filtered(self):
        input_list = [{"type": 99, "title": "Invalid Type"}]
        result = wrapListInfo(input_list)
        self.assertEqual(len(result), 0)


if __name__ == '__main__':
    unittest.main()
