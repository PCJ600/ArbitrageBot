from django.test import TestCase
from app.query.ashare_lof import get_notify_list
from app.notify.notify import notify_handler

# Create your tests here.
class LofTestCase(TestCase):
    def test_notify_list(self):
        result = get_notify_list()
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
            msg = f"{premium_rate}% {apply_status} {redeem_status}"
            title = fund_id
            print("msg: ", msg, " title: ", title)

            # 推送通知功能
            # notify_handler.send_message(msg, title)
