from django.test import TestCase
from app.query.ashare_lof import get_ashare_lof_notify_list
from app.query.qdii import get_qdii_notify_list
from app.query.query_funds import monitor_funds_and_notify
from app.notify.notify import notify_handler

# Create your tests here.
class LofTestCase(TestCase):
    def test_lof_notify_list(self):
        result = get_ashare_lof_notify_list()
        self.assertIsInstance(result, dict)
        self.assertIn('stock_lof', result)
        self.assertIn('index_lof', result)
        self.assertIsInstance(result['stock_lof'], list)
        self.assertIsInstance(result['index_lof'], list)

        all_lofs = result['stock_lof'] + result['index_lof']
        for fund in all_lofs:
            # 验证每个基金的数据结构
            self.assertIsInstance(fund, tuple)
            self.assertEqual(len(fund), 4)
            
            fund_id, premium_rate, apply_status, redeem_status = fund
            self.assertIsInstance(fund_id, str)
            self.assertIsInstance(premium_rate, float)
            self.assertIsInstance(apply_status, str)
            self.assertIsInstance(redeem_status, str)
            
            # 构建消息内容
            msg = f"{premium_rate:.2f}% {apply_status} {redeem_status}"
            title = fund_id
            print(f"LOF基金通知 - 标题: {title}, 内容: {msg}")

            # 推送通知功能
            # notify_handler.send_message(msg, title)

class QdiiTestCase(TestCase):
    def test_qdii_notify_list(self):
        """测试QDII基金通知列表功能"""
        print("begin test qdii notify list")
        
        # 获取通知列表
        result = get_qdii_notify_list()
        
        # 验证返回结果类型和结构
        self.assertIsInstance(result, dict)
        self.assertIn('hk_qdii', result)
        self.assertIn('us_qdii', result)
        self.assertIn('commodity_qdii', result)
        
        self.assertIsInstance(result['hk_qdii'], list)
        self.assertIsInstance(result['us_qdii'], list)
        self.assertIsInstance(result['commodity_qdii'], list)
        
        # 合并所有QDII基金
        all_qdiis = result['hk_qdii'] + result['us_qdii'] + result['commodity_qdii']
        
        # 验证每个基金的数据结构
        for fund in all_qdiis:
            self.assertIsInstance(fund, tuple)
            self.assertEqual(len(fund), 4)
            
            fund_id, premium_rate, apply_status, redeem_status = fund
            self.assertIsInstance(fund_id, str)
            self.assertIsInstance(premium_rate, float)
            self.assertIsInstance(apply_status, str)
            self.assertIsInstance(redeem_status, str)
            
            # 验证数据合理性
            self.assertTrue(len(fund_id) >= 6, f"基金ID长度不足: {fund_id}")
            self.assertTrue(-100 <= premium_rate <= 100, f"溢价率超出合理范围: {premium_rate}")
            self.assertTrue(len(apply_status) > 0, "申购状态不能为空")
            self.assertTrue(len(redeem_status) > 0, "赎回状态不能为空")
            
            # 构建消息内容
            msg = f"{premium_rate:.2f}% {apply_status} {redeem_status}"
            title = f"{fund_id}"
            print(f"QDII基金通知 - 标题: {title}, 内容: {msg}")
            
            # 这里可以添加实际的通知发送逻辑
            #notify_handler.send_message(msg, title)
