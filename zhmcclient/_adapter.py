# Copyright 2016-2017 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
An :term:`Adapter` is a physical adapter card (e.g. OSA-Express adapter,
Crypto adapter) or a logical adapter (e.g. HiperSockets switch).

Adapter resources are contained in :term:`CPC` resources.

Adapters only exist in CPCs that are in DPM mode.

There are four types of Adapters:

1. Network Adapters:
   Network adapters enable communication through different networking
   transport protocols. These network adapters are OSA-Express,
   HiperSockets and RoCE-Express.
   DPM automatically discovers OSA-Express and RoCE-Express adapters
   because they are physical cards that are installed on the CPC.
   In contrast, HiperSockets are logical adapters and must be
   created and configured by an administrator using the 'Create Hipersocket'
   operation (see create_hipersocket()).
   Network Interface Cards (NICs) provide a partition with access to networks.
   Each NIC represents a unique connection between the partition
   and a specific network adapter.

2. Storage Adapters:
   Fibre Channel connections provide high-speed connections between CPCs
   and storage devices.
   DPM automatically discovers any storage adapters installed on the CPC.
   Host bus adapters (HBAs) provide a partition with access to external
   storage area networks (SANs) and devices that are connected to a CPC.
   Each HBA represents a unique connection between the partition
   and a specific storage adapter.

3. Accelerator Adapters:
   Accelerator adapters provide specialized functions to
   improve performance or use of computer resource like the IBM System z
   Enterprise Data Compression (zEDC) feature.
   DPM automatically discovers accelerators that are installed on the CPC.
   An accelerator virtual function provides a partition with access
   to zEDC features that are installed on a CPC.
   Each virtual function represents a unique connection between
   the partition and a physical feature card.

4. Crypto Adapters:
   Crypto adapters provide cryptographic processing functions.
   DPM automatically discovers cryptographic features that are installed
   on the CPC.
"""

from __future__ import absolute_import

import copy

from ._manager import BaseManager
from ._resource import BaseResource
from ._port import PortManager
from ._logging import get_logger, logged_api_call
from ._utils import repr_dict, repr_manager, repr_timestamp

__all__ = ['AdapterManager', 'Adapter']

LOG = get_logger(__name__)


class AdapterManager(BaseManager):
    """
    Manager providing access to the :term:`Adapters <Adapter>` in a particular
    :term:`CPC`.

    Derived from :class:`~zhmcclient.BaseManager`; see there for common methods
    and attributes.

    Objects of this class are not directly created by the user; they are
    accessible via the following instance variable of a
    :class:`~zhmcclient.Cpc` object (in DPM mode):

    * :attr:`~zhmcclient.Cpc.adapters`
    """

    def __init__(self, cpc):
        # This function should not go into the docs.
        # Parameters:
        #   cpc (:class:`~zhmcclient.Cpc`):
        #     CPC defining the scope for this manager.

        # Resource properties that are supported as filter query parameters.
        # If the support for a resource property changes within the set of HMC
        # versions that support this type of resource, this list must be set up
        # for the version of the HMC this session is connected to.
        query_props = [
            'name',
            'adapter-id',
            'adapter-family',
            'type',
            'status',
        ]

        super(AdapterManager, self).__init__(
            resource_class=Adapter,
            session=cpc.manager.session,
            parent=cpc,
            uri_prop='object-uri',
            name_prop='name',
            query_props=query_props)

    @property
    def cpc(self):
        """
        :class:`~zhmcclient.Cpc`: :term:`CPC` defining the scope for this
        manager.
        """
        return self._parent

    @logged_api_call
    def list(self, full_properties=False, filter_args=None):
        """
        List the Adapters in this CPC.

        Authorization requirements:

        * Object-access permission to this CPC.
        * Object-access permission to any Adapter to be included in the result.

        Parameters:

          full_properties (bool):
            Controls whether the full set of resource properties should be
            retrieved, vs. only the short set as returned by the list
            operation.

          filter_args (dict):
            Filter arguments that narrow the list of returned resources to
            those that match the specified filter arguments. For details, see
            :ref:`Filtering`.

            `None` causes no filtering to happen, i.e. all resources are
            returned.

        Returns:

          : A list of :class:`~zhmcclient.Adapter` objects.

        Raises:

          :exc:`~zhmcclient.HTTPError`
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        query_parms, client_filters = self._divide_filter_args(filter_args)

        resources_name = 'adapters'
        uri = '{}/{}{}'.format(self.cpc.uri, resources_name, query_parms)

        resource_obj_list = []
        result = self.session.get(uri)
        if result:
            props_list = result[resources_name]
            for props in props_list:

                resource_obj = self.resource_class(
                    manager=self,
                    uri=props[self._uri_prop],
                    name=props.get(self._name_prop, None),
                    properties=props)

                if self._matches_filters(resource_obj, client_filters):
                    resource_obj_list.append(resource_obj)
                    if full_properties:
                        resource_obj.pull_full_properties()

        self._name_uri_cache.update_from(resource_obj_list)
        return resource_obj_list

    @logged_api_call
    def create_hipersocket(self, properties):
        """
        Create and configure a HiperSockets Adapter in this CPC.

        Authorization requirements:

        * Object-access permission to the scoping CPC.
        * Task permission to the "Create HiperSockets Adapter" task.

        Parameters:

          properties (dict): Initial property values.
            Allowable properties are defined in section 'Request body contents'
            in section 'Create Hipersocket' in the :term:`HMC API` book.

        Returns:

          :class:`~zhmcclient.Adapter`:
            The resource object for the new HiperSockets Adapter.
            The object will have its 'object-uri' property set as returned by
            the HMC, and will also have the input properties set.

        Raises:

          :exc:`~zhmcclient.HTTPError`
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        result = self.session.post(self.cpc.uri + '/adapters', body=properties)
        # There should not be overlaps, but just in case there are, the
        # returned props should overwrite the input props:
        props = copy.deepcopy(properties)
        props.update(result)
        name = props.get(self._name_prop, None)
        uri = props[self._uri_prop]
        adapter = Adapter(self, uri, name, props)
        self._name_uri_cache.update(name, uri)
        return adapter


class Adapter(BaseResource):
    """
    Representation of an :term:`Adapter`.

    Derived from :class:`~zhmcclient.BaseResource`; see there for common
    methods and attributes.

    For the properties of an Adapter, see section 'Data model' in section
    'Adapter object' in the :term:`HMC API` book.

    Objects of this class are not directly created by the user; they are
    returned from creation or list functions on their manager object
    (in this case, :class:`~zhmcclient.AdapterManager`).
    """

    def __init__(self, manager, uri, name=None, properties=None):
        # This function should not go into the docs.
        #   manager (:class:`~zhmcclient.AdapterManager`):
        #     Manager object for this resource object.
        #   uri (string):
        #     Canonical URI path of the resource.
        #   name (string):
        #     Name of the resource.
        #   properties (dict):
        #     Properties to be set for this resource object. May be `None` or
        #     empty.
        assert isinstance(manager, AdapterManager), \
            "Adapter init: Expected manager type %s, got %s" % \
            (AdapterManager, type(manager))
        super(Adapter, self).__init__(manager, uri, name, properties)
        # The manager objects for child resources (with lazy initialization):
        self._ports = None

    @property
    def ports(self):
        """
        :class:`~zhmcclient.PortManager`: Access to the :term:`Ports <Port>` of
        this Adapter.
        """
        # We do here some lazy loading.
        if not self._ports:
            self._ports = PortManager(self)
        return self._ports

    @logged_api_call
    def delete(self):
        """
        Delete this Adapter.

        The Adapter must be a HiperSockets Adapter.

        Authorization requirements:

        * Object-access permission to the HiperSockets Adapter to be deleted.
        * Task permission to the "Delete HiperSockets Adapter" task.

        Raises:

          :exc:`~zhmcclient.HTTPError`
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        self.manager.session.delete(self.uri)
        self.manager._name_uri_cache.delete(
            self.properties.get(self.manager._name_prop, None))

    @logged_api_call
    def update_properties(self, properties):
        """
        Update writeable properties of this Adapter.

        Authorization requirements:

        * Object-access permission to the Adapter.
        * Task permission for the "Adapter Details" task.

        Parameters:

          properties (dict): New values for the properties to be updated.
            Properties not to be updated are omitted.
            Allowable properties are the properties with qualifier (w) in
            section 'Data model' in section 'Adapter object' in the
            :term:`HMC API` book.

        Raises:

          :exc:`~zhmcclient.HTTPError`
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        self.manager.session.post(self.uri, body=properties)
        self.properties.update(copy.deepcopy(properties))
        if self.manager._name_prop in properties:
            self.manager._name_uri_cache.update(self.name, self.uri)

    def __repr__(self):
        """
        Return a string with the state of this Adapter, for debug purposes.
        """
        ret = (
            "{classname} at 0x{id:08x} (\n"
            "  _manager = {_manager_classname} at 0x{_manager_id:08x},\n"
            "  _uri = {_uri!r},\n"
            "  _full_properties = {_full_properties!r},\n"
            "  _properties_timestamp = {_properties_timestamp},\n"
            "  _properties = {_properties}\n"
            "  _ports(lazy) = {_ports}\n"
            ")".format(
                classname=self.__class__.__name__,
                id=id(self),
                _manager_classname=self._manager.__class__.__name__,
                _manager_id=id(self._manager),
                _uri=self._uri,
                _full_properties=self._full_properties,
                _properties_timestamp=repr_timestamp(
                    self._properties_timestamp),
                _properties=repr_dict(self._properties, indent=4),
                _ports=repr_manager(self._ports, indent=2),
            ))
        return ret
