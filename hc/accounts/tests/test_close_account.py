from django.contrib.auth.models import User
from mock import patch

from hc.test import BaseTestCase
from hc.api.models import Check
from hc.payments.models import Subscription


class CloseAccountTestCase(BaseTestCase):

    @patch("hc.payments.models.Subscription.cancel")
    def test_it_works(self, mock_cancel):
        Check.objects.create(user=self.alice, tags="foo a-B_1  baz@")
        Subscription.objects.create(user=self.alice, subscription_id="123")

        self.client.login(username="alice@example.org", password="password")
        r = self.client.post("/accounts/close/")
        self.assertEqual(r.status_code, 302)

        # Alice should be gone
        alices = User.objects.filter(username="alice")
        self.assertFalse(alices.exists())

        # Alice should be gone
        alices = User.objects.filter(username="alice")
        self.assertFalse(alices.exists())

        # Bob's current team should be updated to self
        self.bobs_profile.refresh_from_db()
        self.assertEqual(self.bobs_profile.current_team, self.bobs_profile)

        # Check should be gone
        self.assertFalse(Check.objects.exists())

        # Subscription should have been canceled
        self.assertTrue(mock_cancel.called)

        # Subscription should be gone
        self.assertFalse(Subscription.objects.exists())

    def test_partner_removal_works(self):
        self.client.login(username="bob@example.org", password="password")
        r = self.client.post("/accounts/close/")
        self.assertEqual(r.status_code, 302)

        # Alice should be still present
        self.alice.refresh_from_db()
        self.profile.refresh_from_db()

        # Bob should be gone
        bobs = User.objects.filter(username="bob")
        self.assertFalse(bobs.exists())

    def test_it_rejects_get(self):
        self.client.login(username="bob@example.org", password="password")
        r = self.client.get("/accounts/close/")
        self.assertEqual(r.status_code, 405)
