from __future__ import absolute_import, unicode_literals

from casepro.contacts.models import Field, Group
from casepro.test import BaseCasesTest
from django.core.urlresolvers import reverse


class OrgExtCRUDLTest(BaseCasesTest):
    def setUp(self):
        super(OrgExtCRUDLTest, self).setUp()

        self.unicef.set_banner_text("Howdy (U)Partner!")

    def test_home(self):
        url = reverse('orgs_ext.org_home')

        self.login(self.admin)

        response = self.url_get('unicef', url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Kidus (kidus@unicef.org)")

    def test_edit(self):
        url = reverse('orgs_ext.org_edit')

        self.login(self.admin)

        response = self.url_get('unicef', url)
        self.assertEqual(response.status_code, 200)

        form = response.context['form']

        self.assertEqual(form.initial['name'], "UNICEF")
        self.assertEqual(form.initial['timezone'], "Africa/Kampala")

        self.assertEqual(form.fields['banner_text'].initial, "Howdy (U)Partner!")
        self.assertEqual(form.fields['contact_fields'].choices, [(self.age.pk, "Age (age)"),
                                                                 (self.nickname.pk, "Nickname (nickname)"),
                                                                 (self.state.pk, "State (state)")])
        self.assertEqual(set(form.fields['contact_fields'].initial), {self.age.pk, self.nickname.pk})
        self.assertEqual(form.fields['suspend_groups'].choices, [(self.females.pk, "Females"),
                                                                 (self.males.pk, "Males"),
                                                                 (self.reporters.pk, "Reporters")])
        self.assertEqual(form.fields['suspend_groups'].initial, [self.reporters.pk])

        # test updating
        response = self.url_post('unicef', url, {
            'name': "UNIZEFF", 'timezone': "Africa/Kigali", 'banner_text': "Chill",
            'contact_fields': [self.state.pk], 'suspend_groups': [self.males.pk]
        })

        self.assertEqual(response.status_code, 302)

        self.unicef.refresh_from_db()
        self.unicef._config = None

        self.assertEqual(self.unicef.name, "UNIZEFF")
        self.assertEqual(self.unicef.timezone, "Africa/Kigali")
        self.assertEqual(self.unicef.get_banner_text(), "Chill")

        self.assertEqual(set(Group.get_suspend_from(self.unicef)), {self.males})
        self.assertEqual(set(Field.get_all(self.unicef, visible=True)), {self.state})
