from __future__ import unicode_literals

import six

from casepro.contacts.models import Contact, Group, Field, SAVE_GROUPS_ATTR
from casepro.msgs.models import Label, Message, SAVE_CONTACT_ATTR, SAVE_LABELS_ATTR
from casepro.utils import is_dict_equal
from dash.utils.sync import BaseSyncer, sync_local_to_set, sync_local_to_changes
from itertools import chain
from . import BaseBackend


# no concept of flagging in RapidPro so that is modelled with a label
SYSTEM_LABEL_FLAGGED = "Flagged"


class ContactSyncer(BaseSyncer):
    """
    Syncer for contacts
    """
    model = Contact
    prefetch_related = ('groups',)

    def local_kwargs(self, org, remote):
        if remote.blocked:  # we don't keep blocked contacts
            return None

        # groups and fields are updated via a post save signal handler
        groups = [(g.uuid, g.name) for g in remote.groups]
        fields = {k: v for k, v in six.iteritems(remote.fields) if v is not None}  # don't include none values

        return {
            'org': org,
            'uuid': remote.uuid,
            'name': remote.name,
            'language': remote.language,
            'is_stub': False,
            'fields': fields,
            SAVE_GROUPS_ATTR: groups,
        }

    def update_required(self, local, remote):
        if local.name != remote.name:
            return True

        if local.language != remote.language:
            return True

        if [g.uuid for g in local.groups.all()] != [g.uuid for g in remote.groups]:
            return True

        return not is_dict_equal(local.get_fields(), remote.fields, ignore_none_values=True)

    def delete_local(self, local):
        local.release()


class FieldSyncer(BaseSyncer):
    """
    Syncer for contact fields
    """
    model = Field
    local_id_attr = 'key'
    remote_id_attr = 'key'

    def local_kwargs(self, org, remote):
        return {
            'org': org,
            'key': remote.key,
            'label': remote.label,
            'value_type': self.model.TEMBA_TYPES.get(remote.value_type, self.model.TYPE_TEXT)
        }

    def update_required(self, local, remote):
        return local.label != remote.label or local.value_type != self.model.TEMBA_TYPES.get(remote.value_type)


class GroupSyncer(BaseSyncer):
    """
    Syncer for contact groups
    """
    model = Group

    def local_kwargs(self, org, remote):
        return {
            'org': org,
            'uuid': remote.uuid,
            'name': remote.name,
            'count': remote.count,
        }

    def update_required(self, local, remote):
        return local.name != remote.name or local.count != remote.count


class LabelSyncer(BaseSyncer):
    """
    Syncer for message labels
    """
    model = Label

    def local_kwargs(self, org, remote):
        # don't create locally if this is just the pseudo-label for flagging
        if remote.name == SYSTEM_LABEL_FLAGGED:
            return None

        return {
            'org': org,
            'uuid': remote.uuid,
            'name': remote.name,
        }

    def update_required(self, local, remote):
        return local.name != remote.name


class MessageSyncer(BaseSyncer):
    """
    Syncer for messages
    """
    model = Message
    local_id_attr = 'backend_id'
    remote_id_attr = 'id'
    select_related = ('contact',)
    prefetch_related = ('labels',)

    def __init__(self, as_handled=False):
        self.as_handled = as_handled

    def local_kwargs(self, org, remote):
        if remote.visibility == 'deleted':
            return None

        # labels are updated via a post save signal handler
        labels = [(l.uuid, l.name) for l in remote.labels if l.name != SYSTEM_LABEL_FLAGGED]

        kwargs = {
            'org': org,
            'backend_id': remote.id,
            'type': 'I' if remote.type == 'inbox' else 'F',
            'text': remote.text,
            'is_flagged': SYSTEM_LABEL_FLAGGED in [l.name for l in remote.labels],
            'is_archived': (remote.visibility == 'archived'),
            'created_on': remote.created_on,
            SAVE_CONTACT_ATTR: (remote.contact.uuid, remote.contact.name),
            SAVE_LABELS_ATTR: labels,
        }

        if self.as_handled:
            kwargs['is_handled'] = True

        return kwargs

    def update_required(self, local, remote):
        if local.is_flagged != (SYSTEM_LABEL_FLAGGED in [l.name for l in remote.labels]):
            return True

        if local.is_archived and remote.visibility != 'archived':
            return True

        local_label_uuids = [l.uuid for l in local.labels.all()]
        incoming_label_uuids = [l.uuid for l in remote.labels if l.name != SYSTEM_LABEL_FLAGGED]

        return local_label_uuids != incoming_label_uuids

    def delete_local(self, local):
        local.release()


class RapidProBackend(BaseBackend):
    """
    RapidPro instance as a backend
    """
    @staticmethod
    def _get_client(org, api_version):
        return org.get_temba_client(api_version=api_version)

    def pull_contacts(self, org, modified_after, modified_before, progress_callback=None):
        client = self._get_client(org, 2)

        # all contacts created or modified in RapidPro in the time window
        active_query = client.get_contacts(after=modified_after, before=modified_before)
        fetches = active_query.iterfetches(retry_on_rate_exceed=True)

        # all contacts deleted in RapidPro in the same time window
        deleted_query = client.get_contacts(deleted=True, after=modified_after, before=modified_before)
        deleted_fetches = deleted_query.iterfetches(retry_on_rate_exceed=True)

        return sync_local_to_changes(org, ContactSyncer(), fetches, deleted_fetches, progress_callback)

    def pull_fields(self, org):
        client = self._get_client(org, 2)
        incoming_objects = client.get_fields().all(retry_on_rate_exceed=True)

        return sync_local_to_set(org, FieldSyncer(), incoming_objects)

    def pull_groups(self, org):
        client = self._get_client(org, 2)
        incoming_objects = client.get_groups().all(retry_on_rate_exceed=True)

        return sync_local_to_set(org, GroupSyncer(), incoming_objects)

    def pull_labels(self, org):
        client = self._get_client(org, 2)
        incoming_objects = client.get_labels().all(retry_on_rate_exceed=True)

        return sync_local_to_set(org, LabelSyncer(), incoming_objects)

    def pull_messages(self, org, modified_after, modified_before, as_handled=False, progress_callback=None):
        client = self._get_client(org, 2)

        # all incoming messages created or modified in RapidPro in the time window
        query = client.get_messages(folder='incoming', after=modified_after, before=modified_before)
        fetches = query.iterfetches(retry_on_rate_exceed=True)

        return sync_local_to_changes(org, MessageSyncer(as_handled), fetches, [], progress_callback)

    def create_label(self, org, name):
        client = self._get_client(org, 1)
        temba_labels = client.get_labels(name=name)  # gets all partial name matches
        temba_labels = [l for l in temba_labels if l.name.lower() == name.lower()]

        if temba_labels:
            remote = temba_labels[0]
        else:
            remote = client.create_label(name)

        return remote.uuid

    def add_to_group(self, org, contact, group):
        client = self._get_client(org, 1)
        client.add_contacts([contact.uuid], group_uuid=group.uuid)

    def remove_from_group(self, org, contact, group):
        client = self._get_client(org, 1)
        client.remove_contacts([contact.uuid], group_uuid=group.uuid)

    def stop_runs(self, org, contact):
        client = self._get_client(org, 1)
        client.expire_contacts([contact.uuid])

    def label_messages(self, org, messages, label):
        if messages:
            client = self._get_client(org, 1)
            client.label_messages(messages=[m.backend_id for m in messages], label_uuid=label.uuid)

    def archive_messages(self, org, messages):
        if messages:
            client = self._get_client(org, 1)
            client.archive_messages(messages=[m.backend_id for m in messages])

    def archive_contact_messages(self, org, contact):
        client = self._get_client(org, 1)

        # TODO add to contact action endpoint in RapidPro for archiving a contact's messages as this is inefficient
        messages = client.get_messages(contacts=[contact.uuid], direction='I', statuses=['H'], _types=['I'], archived=False)
        if messages:
            client.archive_messages(messages=[m.id for m in messages])

    def restore_messages(self, org, messages):
        if messages:
            client = self._get_client(org, 1)
            client.unarchive_messages(messages=[m.backend_id for m in messages])

    def flag_messages(self, org, messages):
        if messages:
            client = self._get_client(org, 1)
            client.label_messages(messages=[m.backend_id for m in messages], label=SYSTEM_LABEL_FLAGGED)

    def unflag_messages(self, org, messages):
        if messages:
            client = self._get_client(org, 1)
            client.unlabel_messages(messages=[m.backend_id for m in messages], label=SYSTEM_LABEL_FLAGGED)