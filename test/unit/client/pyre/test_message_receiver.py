import unittest
import uuid

from colmena.client.pyre import receiver_selector

one = uuid.uuid4()
two = uuid.uuid4()

class TestMessageReceiver(unittest.TestCase):

    def test_explore_when_no_recipients_are_present(self):
        lls = receiver_selector.LeastLatencySelector(epsilon=1)
        selected = lls.select_recipient([one])
        self.assertEqual(selected, one)

    def test_exploit_when_one_recipient_has_recorded_latency(self):
        lls = receiver_selector.LeastLatencySelector(epsilon=0)
        lls.update_estimate(str(one), 125)
        selected = lls.select_recipient([one, two])
        self.assertEqual(selected, one)
        self.assertEqual(lls.latency_estimates[str(one)], 125)

    def test_exploit_when_no_recorded_latencies(self):
        lls = receiver_selector.LeastLatencySelector(epsilon=0)
        selected = lls.select_recipient([one])
        self.assertEqual(selected, one)

    def test_exploit_when_recipient_is_no_longer_part_of_current_peers(self):
        lls = receiver_selector.LeastLatencySelector(epsilon=0)
        lls.update_estimate(str(one), 125)
        selected = lls.select_recipient([two])
        self.assertEqual(selected, two)

    def test_update_estimate_using_ema(self):
        lls = receiver_selector.LeastLatencySelector(epsilon=0, alpha=0.9)
        lls.update_estimate(str(one), 100)
        self.assertEqual(lls.latency_estimates[str(one)], 100)
        lls.update_estimate(str(one), 200)
        self.assertEqual(lls.latency_estimates[str(one)], 190)
