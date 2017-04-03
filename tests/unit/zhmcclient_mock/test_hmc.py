#!/usr/bin/env python
# Copyright 2016 IBM Corp. All Rights Reserved.
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
Unit tests for _hmc module of the zhmcclient_mock package.
"""

from __future__ import absolute_import, print_function

import unittest
import re

from zhmcclient_mock._hmc import FakedHmc, \
    FakedActivationProfileManager, FakedActivationProfile, \
    FakedAdapterManager, FakedAdapter, \
    FakedCpcManager, FakedCpc, \
    FakedHbaManager, FakedHba, \
    FakedLparManager, FakedLpar, \
    FakedNicManager, FakedNic, \
    FakedPartitionManager, FakedPartition, \
    FakedPortManager, FakedPort, \
    FakedVirtualFunctionManager, FakedVirtualFunction, \
    FakedVirtualSwitchManager, FakedVirtualSwitch, \
    FakedBaseManager, FakedBaseResource


class FakedHmcTests(unittest.TestCase):
    """All tests for the zhmcclient_mock.FakedHmc class."""

    def setUp(self):
        self.hmc = FakedHmc('fake-hmc', '2.13.1', '1.8')

    def test_repr(self):

        # The test approach is to check the repr() result for each attribute
        # that is shown in the result, but leaving some flexibility in how that
        # is formatted.

        # Bring everything into one line, because regexp is line-oriented.
        act_repr = repr(self.hmc).replace('\n', '\\n')

        self.assertRegexpMatches(
            act_repr,
            r'.*FakedHmc\s+at\s+0x{id:08x}\s+\(\\n.*'.
            format(id=id(self.hmc)))

        self.assertRegexpMatches(
            act_repr,
            r'.*\shmc_name\s*=\s*{hmc_name!r}\\n.*'.
            format(hmc_name=self.hmc.hmc_name))

        self.assertRegexpMatches(
            act_repr,
            r'.*\shmc_version\s*=\s*{hmc_version!r}\\n.*'.
            format(hmc_version=self.hmc.hmc_version))

        self.assertRegexpMatches(
            act_repr,
            r'.*\sapi_version\s*=\s*{api_version!r}\\n.*'.
            format(api_version=self.hmc.api_version))

        self.assertRegexpMatches(
            act_repr,
            r'.*\scpcs\s*=\s*FakedCpcManager\s.*')
        # TODO: Check content of `cpcs`

        self.assertRegexpMatches(
            act_repr,
            r'.*\s_resources\s*=\s.*')
        # TODO: Check content of `_resources`

    def test_hmc(self):
        self.assertEqual(self.hmc.hmc_name, 'fake-hmc')
        self.assertEqual(self.hmc.hmc_version, '2.13.1')
        self.assertEqual(self.hmc.api_version, '1.8')
        self.assertIsInstance(self.hmc.cpcs, FakedCpcManager)

        # the function to be tested:
        cpcs = self.hmc.cpcs.list()

        self.assertEqual(len(cpcs), 0)

    def test_hmc_1_cpc(self):
        cpc1_in_props = {'name': 'cpc1'}

        # the function to be tested:
        cpc1 = self.hmc.cpcs.add(cpc1_in_props)

        cpc1_out_props = cpc1_in_props.copy()
        cpc1_out_props.update({
            'object-id': cpc1.oid,
            'object-uri': cpc1.uri,
            'dpm-enabled': False,
            'is-ensemble-member': False,
            'status': 'operating',
        })

        # the function to be tested:
        cpcs = self.hmc.cpcs.list()

        self.assertEqual(len(cpcs), 1)
        self.assertEqual(cpcs[0], cpc1)

        self.assertIsInstance(cpc1, FakedCpc)
        self.assertEqual(cpc1.properties, cpc1_out_props)
        self.assertEqual(cpc1.manager, self.hmc.cpcs)

    def test_hmc_2_cpcs(self):
        cpc1_in_props = {'name': 'cpc1'}

        # the function to be tested:
        cpc1 = self.hmc.cpcs.add(cpc1_in_props)

        cpc1_out_props = cpc1_in_props.copy()
        cpc1_out_props.update({
            'object-id': cpc1.oid,
            'object-uri': cpc1.uri,
            'dpm-enabled': False,
            'is-ensemble-member': False,
            'status': 'operating',
        })

        cpc2_in_props = {'name': 'cpc2'}

        # the function to be tested:
        cpc2 = self.hmc.cpcs.add(cpc2_in_props)

        cpc2_out_props = cpc2_in_props.copy()
        cpc2_out_props.update({
            'object-id': cpc2.oid,
            'object-uri': cpc2.uri,
            'dpm-enabled': False,
            'is-ensemble-member': False,
            'status': 'operating',
        })

        # the function to be tested:
        cpcs = self.hmc.cpcs.list()

        self.assertEqual(len(cpcs), 2)
        # We expect the order of addition to be maintained:
        self.assertEqual(cpcs[0], cpc1)
        self.assertEqual(cpcs[1], cpc2)

        self.assertIsInstance(cpc1, FakedCpc)
        self.assertEqual(cpc1.properties, cpc1_out_props)
        self.assertEqual(cpc1.manager, self.hmc.cpcs)

        self.assertIsInstance(cpc2, FakedCpc)
        self.assertEqual(cpc2.properties, cpc2_out_props)
        self.assertEqual(cpc2.manager, self.hmc.cpcs)

    def test_res_dict(self):
        cpc1_in_props = {'name': 'cpc1'}
        adapter1_in_props = {'name': 'osa1', 'adapter-family': 'hipersockets'}
        port1_in_props = {'name': 'osa1_1'}

        rd = {
            'cpcs': [
                {
                    'properties': cpc1_in_props,
                    'adapters': [
                        {
                            'properties': adapter1_in_props,
                            'ports': [
                                {'properties': port1_in_props},
                            ],
                        },
                    ],
                },
            ]
        }

        # the function to be tested:
        self.hmc.add_resources(rd)

        cpcs = self.hmc.cpcs.list()

        self.assertEqual(len(cpcs), 1)

        cpc1 = cpcs[0]
        cpc1_out_props = cpc1_in_props.copy()
        cpc1_out_props.update({
            'object-id': cpc1.oid,
            'object-uri': cpc1.uri,
            'dpm-enabled': False,
            'is-ensemble-member': False,
            'status': 'operating',
        })
        self.assertIsInstance(cpc1, FakedCpc)
        self.assertEqual(cpc1.properties, cpc1_out_props)
        self.assertEqual(cpc1.manager, self.hmc.cpcs)

        cpc1_adapters = cpc1.adapters.list()

        self.assertEqual(len(cpc1_adapters), 1)
        adapter1 = cpc1_adapters[0]

        adapter1_ports = adapter1.ports.list()

        self.assertEqual(len(adapter1_ports), 1)
        port1 = adapter1_ports[0]

        adapter1_out_props = adapter1_in_props.copy()
        adapter1_out_props.update({
            'object-id': adapter1.oid,
            'object-uri': adapter1.uri,
            'status': 'active',
            'network-port-uris': [port1.uri],
        })
        self.assertIsInstance(adapter1, FakedAdapter)
        self.assertEqual(adapter1.properties, adapter1_out_props)
        self.assertEqual(adapter1.manager, cpc1.adapters)

        port1_out_props = port1_in_props.copy()
        port1_out_props.update({
            'element-id': port1.oid,
            'element-uri': port1.uri,
        })
        self.assertIsInstance(port1, FakedPort)
        self.assertEqual(port1.properties, port1_out_props)
        self.assertEqual(port1.manager, adapter1.ports)


class FakedBaseTests(unittest.TestCase):
    """All tests for the FakedBaseManager and FakedBaseResource classes."""

    def setUp(self):
        self.hmc = FakedHmc('fake-hmc', '2.13.1', '1.8')
        self.cpc1_in_props = {
            # All properties that are otherwise defaulted (but with non-default
            # values), plus 'name'.
            'object-id': '42',
            'object-uri': '/api/cpcs/42',
            'dpm-enabled': True,
            'is-ensemble-member': False,
            'status': 'service',
            'name': 'cpc1',
        }
        rd = {
            'cpcs': [
                {
                    'properties': self.cpc1_in_props,
                },
            ]
        }
        self.hmc.add_resources(rd)
        self.cpc_manager = self.hmc.cpcs
        self.cpc_resource = self.hmc.cpcs.list()[0]
        self.cpc1_out_props = self.cpc1_in_props.copy()

    def test_manager_attr(self):
        """Test FakedBaseManager attributes."""

        self.assertIsInstance(self.cpc_manager, FakedBaseManager)

        self.assertEqual(self.cpc_manager.hmc, self.hmc)
        self.assertEqual(self.cpc_manager.parent, self.hmc)
        self.assertEqual(self.cpc_manager.resource_class, FakedCpc)
        self.assertEqual(self.cpc_manager.base_uri, '/api/cpcs')
        self.assertEqual(self.cpc_manager.oid_prop, 'object-id')
        self.assertEqual(self.cpc_manager.uri_prop, 'object-uri')

    def test_resource_attr(self):
        """Test FakedBaseResource attributes."""

        self.assertIsInstance(self.cpc_resource, FakedBaseResource)

        self.assertEqual(self.cpc_resource.manager, self.cpc_manager)
        self.assertEqual(self.cpc_resource.properties, self.cpc1_out_props)
        self.assertEqual(self.cpc_resource.oid,
                         self.cpc1_out_props['object-id'])
        self.assertEqual(self.cpc_resource.uri,
                         self.cpc1_out_props['object-uri'])

    def test_manager_repr(self):
        """Test FakedBaseManager.__repr__()."""

        # The test approach is to check the repr() result for each attribute
        # that is shown in the result, but leaving some flexibility in how that
        # is formatted.

        # Bring everything into one line, because regexp is line-oriented.
        act_repr = repr(self.cpc_manager).replace('\n', '\\n')

        self.assertRegexpMatches(
            act_repr,
            r'.*{classname}\s+at\s+0x{id:08x}\s+\(\\n.*'.
            format(classname=self.cpc_manager.__class__.__name__,
                   id=id(self.cpc_manager)))

        self.assertRegexpMatches(
            act_repr,
            r'.*\s_hmc\s*=\s*{hmc_classname}\s+at\s+0x{hmc_id:08x}\\n.*'.
            format(hmc_classname=self.cpc_manager.hmc.__class__.__name__,
                   hmc_id=id(self.cpc_manager.hmc)))

        self.assertRegexpMatches(
            act_repr,
            r'.*\s_parent\s*=\s*{p_classname}\s+at\s+0x{p_id:08x}\\n.*'.
            format(p_classname=self.cpc_manager.parent.__class__.__name__,
                   p_id=id(self.cpc_manager.parent)))

        m = re.match(r'.*\s_resource_class\s*=\s*([^\\]+)\\n.*', act_repr)
        if not m:
            raise AssertionError("'_resource_class = ...' did not match "
                                 "in: {!r}".format(act_repr))
        act_resource_class = m.group(1)
        self.assertEqual(act_resource_class,
                         repr(self.cpc_manager.resource_class))

        self.assertRegexpMatches(
            act_repr,
            r'.*\s_base_uri\s*=\s*{_base_uri!r}\\n.*'.
            format(_base_uri=self.cpc_manager.base_uri))

        self.assertRegexpMatches(
            act_repr,
            r'.*\s_oid_prop\s*=\s*{_oid_prop!r}\\n.*'.
            format(_oid_prop=self.cpc_manager.oid_prop))

        self.assertRegexpMatches(
            act_repr,
            r'.*\s_uri_prop\s*=\s*{_uri_prop!r}\\n.*'.
            format(_uri_prop=self.cpc_manager.uri_prop))

        self.assertRegexpMatches(
            act_repr,
            r'.*\s_resources\s*=\s.*')
        # TODO: Check content of `_resources`

    def test_resource_repr(self):
        """Test FakedBaseResource.__repr__()."""

        # The test approach is to check the repr() result for each attribute
        # that is shown in the result, but leaving some flexibility in how that
        # is formatted.

        # Bring everything into one line, because regexp is line-oriented.
        act_repr = repr(self.cpc_resource).replace('\n', '\\n')

        self.assertRegexpMatches(
            act_repr,
            r'.*{classname}\s+at\s+0x{id:08x}\s+\(\\n.*'.
            format(classname=self.cpc_resource.__class__.__name__,
                   id=id(self.cpc_resource)))

        self.assertRegexpMatches(
            act_repr,
            r'.*\s_manager\s*=\s*{m_classname}\s+at\s+0x{m_id:08x}\\n.*'.
            format(m_classname=self.cpc_resource.manager.__class__.__name__,
                   m_id=id(self.cpc_resource.manager)))

        self.assertRegexpMatches(
            act_repr,
            r'.*\s_manager._parent._uri\s*=\s*{p_uri!r}\\n.*'.
            format(p_uri=self.cpc_resource.manager.parent.uri))

        self.assertRegexpMatches(
            act_repr,
            r'.*\s_uri\s*=\s*{_uri!r}\\n.*'.
            format(_uri=self.cpc_resource.uri))

        self.assertRegexpMatches(
            act_repr,
            r'.*\s_properties\s*=\s.*')
        # TODO: Check content of `_properties`


class FakedActivationProfileTests(unittest.TestCase):
    """All tests for the FakedActivationProfileManager and
    FakedActivationProfile classes."""

    def setUp(self):
        self.hmc = FakedHmc('fake-hmc', '2.13.1', '1.8')
        self.cpc1_in_props = {'name': 'cpc1'}
        self.resetprofile1_in_props = {'name': 'resetprofile1'}
        self.imageprofile1_in_props = {'name': 'imageprofile1'}
        self.loadprofile1_in_props = {'name': 'loadprofile1'}
        rd = {
            'cpcs': [
                {
                    'properties': self.cpc1_in_props,
                    'reset_activation_profiles': [
                        {'properties': self.resetprofile1_in_props},
                    ],
                    'image_activation_profiles': [
                        {'properties': self.imageprofile1_in_props},
                    ],
                    'load_activation_profiles': [
                        {'properties': self.loadprofile1_in_props},
                    ],
                },
            ]
        }
        # This already uses add() of FakedActivationProfileManager:
        self.hmc.add_resources(rd)

    def test_profiles_attr(self):
        """Test CPC '*_activation_profiles' attributes."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]

        # Test reset activation profiles

        self.assertIsInstance(cpc1.reset_activation_profiles,
                              FakedActivationProfileManager)
        self.assertEqual(cpc1.reset_activation_profiles.profile_type, 'reset')
        self.assertRegexpMatches(cpc1.reset_activation_profiles.base_uri,
                                 r'/api/cpcs/[^/]+/reset-activation-profiles')

        # Test image activation profiles

        self.assertIsInstance(cpc1.image_activation_profiles,
                              FakedActivationProfileManager)
        self.assertEqual(cpc1.image_activation_profiles.profile_type, 'image')
        self.assertRegexpMatches(cpc1.image_activation_profiles.base_uri,
                                 r'/api/cpcs/[^/]+/image-activation-profiles')

        # Test load activation profiles

        self.assertIsInstance(cpc1.load_activation_profiles,
                              FakedActivationProfileManager)
        self.assertEqual(cpc1.load_activation_profiles.profile_type, 'load')
        self.assertRegexpMatches(cpc1.load_activation_profiles.base_uri,
                                 r'/api/cpcs/[^/]+/load-activation-profiles')

    def test_profiles_list(self):
        """Test list() of FakedActivationProfileManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]

        # Test reset activation profiles

        resetprofiles = cpc1.reset_activation_profiles.list()

        self.assertEqual(len(resetprofiles), 1)
        resetprofile1 = resetprofiles[0]
        resetprofile1_out_props = self.resetprofile1_in_props.copy()
        resetprofile1_out_props.update({
            'element-id': resetprofile1.oid,
            'element-uri': resetprofile1.uri,
        })
        self.assertIsInstance(resetprofile1, FakedActivationProfile)
        self.assertEqual(resetprofile1.properties, resetprofile1_out_props)
        self.assertEqual(resetprofile1.manager, cpc1.reset_activation_profiles)

        # Test image activation profiles

        imageprofiles = cpc1.image_activation_profiles.list()

        self.assertEqual(len(imageprofiles), 1)
        imageprofile1 = imageprofiles[0]
        imageprofile1_out_props = self.imageprofile1_in_props.copy()
        imageprofile1_out_props.update({
            'element-id': imageprofile1.oid,
            'element-uri': imageprofile1.uri,
        })
        self.assertIsInstance(imageprofile1, FakedActivationProfile)
        self.assertEqual(imageprofile1.properties, imageprofile1_out_props)
        self.assertEqual(imageprofile1.manager, cpc1.image_activation_profiles)

        # Test load activation profiles

        loadprofiles = cpc1.load_activation_profiles.list()

        self.assertEqual(len(loadprofiles), 1)
        loadprofile1 = loadprofiles[0]
        loadprofile1_out_props = self.loadprofile1_in_props.copy()
        loadprofile1_out_props.update({
            'element-id': loadprofile1.oid,
            'element-uri': loadprofile1.uri,
        })
        self.assertIsInstance(loadprofile1, FakedActivationProfile)
        self.assertEqual(loadprofile1.properties, loadprofile1_out_props)
        self.assertEqual(loadprofile1.manager, cpc1.load_activation_profiles)

    def test_profiles_add(self):
        """Test add() of FakedActivationProfileManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        resetprofiles = cpc1.reset_activation_profiles.list()
        self.assertEqual(len(resetprofiles), 1)

        resetprofile2_in_props = {'name': 'resetprofile2'}

        # the function to be tested:
        new_resetprofile = cpc1.reset_activation_profiles.add(
            resetprofile2_in_props)

        resetprofiles = cpc1.reset_activation_profiles.list()
        self.assertEqual(len(resetprofiles), 2)

        resetprofile2 = [p for p in resetprofiles
                         if p.properties['name'] ==
                         resetprofile2_in_props['name']][0]

        self.assertEqual(new_resetprofile.properties, resetprofile2.properties)
        self.assertEqual(new_resetprofile.manager, resetprofile2.manager)

        resetprofile2_out_props = resetprofile2_in_props.copy()
        resetprofile2_out_props.update({
            'element-id': resetprofile2.oid,
            'element-uri': resetprofile2.uri,
        })
        self.assertIsInstance(resetprofile2, FakedActivationProfile)
        self.assertEqual(resetprofile2.properties, resetprofile2_out_props)
        self.assertEqual(resetprofile2.manager, cpc1.reset_activation_profiles)

        # Because we know that the image and load profile managers are of the
        # same class, we don't need to test them.

    def test_profiles_remove(self):
        """Test remove() of FakedActivationProfileManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        resetprofiles = cpc1.reset_activation_profiles.list()
        resetprofile1 = resetprofiles[0]
        self.assertEqual(len(resetprofiles), 1)

        # the function to be tested:
        cpc1.reset_activation_profiles.remove(resetprofile1.oid)

        resetprofiles = cpc1.reset_activation_profiles.list()
        self.assertEqual(len(resetprofiles), 0)

        # Because we know that the image and load profile managers are of the
        # same class, we don't need to test them.


class FakedAdapterTests(unittest.TestCase):
    """All tests for the FakedAdapterManager and FakedAdapter classes."""

    def setUp(self):
        self.hmc = FakedHmc('fake-hmc', '2.13.1', '1.8')
        self.cpc1_in_props = {'name': 'cpc1'}
        self.adapter1_in_props = {'name': 'adapter1', 'type': 'roce'}
        rd = {
            'cpcs': [
                {
                    'properties': self.cpc1_in_props,
                    'adapters': [
                        {'properties': self.adapter1_in_props},
                    ],
                },
            ]
        }
        # This already uses add() of FakedAdapterManager:
        self.hmc.add_resources(rd)

    def test_adapters_attr(self):
        """Test CPC 'adapters' attribute."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]

        self.assertIsInstance(cpc1.adapters, FakedAdapterManager)
        self.assertRegexpMatches(cpc1.adapters.base_uri, r'/api/adapters')

    def test_adapters_list(self):
        """Test list() of FakedAdapterManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]

        # the function to be tested:
        adapters = cpc1.adapters.list()

        self.assertEqual(len(adapters), 1)
        adapter1 = adapters[0]
        adapter1_out_props = self.adapter1_in_props.copy()
        adapter1_out_props.update({
            'object-id': adapter1.oid,
            'object-uri': adapter1.uri,
            'status': 'active',
            'adapter-family': 'roce',
            'network-port-uris': [],
        })
        self.assertIsInstance(adapter1, FakedAdapter)
        self.assertEqual(adapter1.properties, adapter1_out_props)
        self.assertEqual(adapter1.manager, cpc1.adapters)

        # Quick check of child resources:
        self.assertIsInstance(adapter1.ports, FakedPortManager)

    def test_adapters_add(self):
        """Test add() of FakedAdapterManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        adapters = cpc1.adapters.list()
        self.assertEqual(len(adapters), 1)

        adapter2_in_props = {'name': 'adapter2', 'adapter-family': 'ficon'}

        # the function to be tested:
        new_adapter = cpc1.adapters.add(
            adapter2_in_props)

        adapters = cpc1.adapters.list()
        self.assertEqual(len(adapters), 2)

        adapter2 = [a for a in adapters
                    if a.properties['name'] == adapter2_in_props['name']][0]

        self.assertEqual(new_adapter.properties, adapter2.properties)
        self.assertEqual(new_adapter.manager, adapter2.manager)

        adapter2_out_props = adapter2_in_props.copy()
        adapter2_out_props.update({
            'object-id': adapter2.oid,
            'object-uri': adapter2.uri,
            'status': 'active',
            'storage-port-uris': [],
        })
        self.assertIsInstance(adapter2, FakedAdapter)
        self.assertEqual(adapter2.properties, adapter2_out_props)
        self.assertEqual(adapter2.manager, cpc1.adapters)

    def test_adapters_remove(self):
        """Test remove() of FakedAdapterManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        adapters = cpc1.adapters.list()
        adapter1 = adapters[0]
        self.assertEqual(len(adapters), 1)

        # the function to be tested:
        cpc1.adapters.remove(adapter1.oid)

        adapters = cpc1.adapters.list()
        self.assertEqual(len(adapters), 0)


class FakedCpcTests(unittest.TestCase):
    """All tests for the FakedCpcManager and FakedCpc classes."""

    def setUp(self):
        self.hmc = FakedHmc('fake-hmc', '2.13.1', '1.8')
        self.cpc1_in_props = {'name': 'cpc1'}
        rd = {
            'cpcs': [
                {
                    'properties': self.cpc1_in_props,
                },
            ]
        }
        # This already uses add() of FakedCpcManager:
        self.hmc.add_resources(rd)

    def test_cpcs_attr(self):
        """Test HMC 'cpcs' attribute."""
        self.assertIsInstance(self.hmc.cpcs, FakedCpcManager)
        self.assertRegexpMatches(self.hmc.cpcs.base_uri, r'/api/cpcs')

    def test_cpcs_list(self):
        """Test list() of FakedCpcManager."""

        # the function to be tested:
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]

        cpc1_out_props = self.cpc1_in_props.copy()
        cpc1_out_props.update({
            'object-id': cpc1.oid,
            'object-uri': cpc1.uri,
            'dpm-enabled': False,
            'is-ensemble-member': False,
            'status': 'operating',
        })
        self.assertIsInstance(cpc1, FakedCpc)
        self.assertEqual(cpc1.properties, cpc1_out_props)
        self.assertEqual(cpc1.manager, self.hmc.cpcs)

        # Quick check of child resources:
        self.assertIsInstance(cpc1.lpars, FakedLparManager)
        self.assertIsInstance(cpc1.partitions, FakedPartitionManager)
        self.assertIsInstance(cpc1.adapters, FakedAdapterManager)
        self.assertIsInstance(cpc1.virtual_switches, FakedVirtualSwitchManager)
        self.assertIsInstance(cpc1.reset_activation_profiles,
                              FakedActivationProfileManager)
        self.assertIsInstance(cpc1.image_activation_profiles,
                              FakedActivationProfileManager)
        self.assertIsInstance(cpc1.load_activation_profiles,
                              FakedActivationProfileManager)

    def test_cpcs_add(self):
        """Test add() of FakedCpcManager."""
        cpcs = self.hmc.cpcs.list()
        self.assertEqual(len(cpcs), 1)

        cpc2_in_props = {'name': 'cpc2'}

        # the function to be tested:
        new_cpc = self.hmc.cpcs.add(cpc2_in_props)

        cpcs = self.hmc.cpcs.list()
        self.assertEqual(len(cpcs), 2)

        cpc2 = [cpc for cpc in cpcs
                if cpc.properties['name'] == cpc2_in_props['name']][0]

        self.assertEqual(new_cpc.properties, cpc2.properties)
        self.assertEqual(new_cpc.manager, cpc2.manager)

        cpc2_out_props = cpc2_in_props.copy()
        cpc2_out_props.update({
            'object-id': cpc2.oid,
            'object-uri': cpc2.uri,
            'dpm-enabled': False,
            'is-ensemble-member': False,
            'status': 'operating',
        })
        self.assertIsInstance(cpc2, FakedCpc)
        self.assertEqual(cpc2.properties, cpc2_out_props)
        self.assertEqual(cpc2.manager, self.hmc.cpcs)

    def test_cpcs_remove(self):
        """Test remove() of FakedCpcManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        self.assertEqual(len(cpcs), 1)

        # the function to be tested:
        self.hmc.cpcs.remove(cpc1.oid)

        cpcs = self.hmc.cpcs.list()
        self.assertEqual(len(cpcs), 0)


class FakedHbaTests(unittest.TestCase):
    """All tests for the FakedHbaManager and FakedHba classes."""

    def setUp(self):
        self.hmc = FakedHmc('fake-hmc', '2.13.1', '1.8')
        self.cpc1_in_props = {'name': 'cpc1'}
        self.partition1_in_props = {'name': 'partition1'}
        self.adapter1_in_props = {
            'object-id': '1',
            'name': 'fcp1',
            'type': 'fcp',
        }
        self.port1_in_props = {
            'element-id': '1',
            'name': 'port1',
        }
        self.hba1_in_props = {
            'name': 'hba1',
            'adapter-port-uri': '/api/adapters/1/storage-ports/1',
        }
        rd = {
            'cpcs': [
                {
                    'properties': self.cpc1_in_props,
                    'partitions': [
                        {
                            'properties': self.partition1_in_props,
                            'hbas': [
                                {'properties': self.hba1_in_props},
                            ],
                        },
                    ],
                    'adapters': [
                        {
                            'properties': self.adapter1_in_props,
                            'ports': [
                                {'properties': self.port1_in_props},
                            ],
                        },
                    ],
                },
            ]
        }
        # This already uses add() of FakedHbaManager:
        self.hmc.add_resources(rd)

    def test_hbas_attr(self):
        """Test Partition 'hbas' attribute."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        partitions = cpc1.partitions.list()
        partition1 = partitions[0]

        self.assertIsInstance(partition1.hbas, FakedHbaManager)
        self.assertRegexpMatches(partition1.hbas.base_uri,
                                 r'/api/partitions/[^/]+/hbas')

    def test_hbas_list(self):
        """Test list() of FakedHbaManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        partitions = cpc1.partitions.list()
        partition1 = partitions[0]

        # the function to be tested:
        hbas = partition1.hbas.list()

        self.assertEqual(len(hbas), 1)
        hba1 = hbas[0]
        hba1_out_props = self.hba1_in_props.copy()
        hba1_out_props.update({
            'element-id': hba1.oid,
            'element-uri': hba1.uri,
            'device-number': hba1.properties['device-number'],
            'wwpn': hba1.properties['wwpn'],
        })
        self.assertIsInstance(hba1, FakedHba)
        self.assertEqual(hba1.properties, hba1_out_props)
        self.assertEqual(hba1.manager, partition1.hbas)

    def test_hbas_add(self):
        """Test add() of FakedHbaManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        partitions = cpc1.partitions.list()
        partition1 = partitions[0]
        hbas = partition1.hbas.list()
        self.assertEqual(len(hbas), 1)

        hba2_in_props = {
            'element-id': '2',
            'name': 'hba2',
            'adapter-port-uri': '/api/adapters/1/storage-ports/1',
            'device-number': '8001',
            'wwpn': 'AFFEAFFE00008001',
        }

        # the function to be tested:
        new_hba = partition1.hbas.add(
            hba2_in_props)

        hbas = partition1.hbas.list()
        self.assertEqual(len(hbas), 2)

        hba2 = [hba for hba in hbas
                if hba.properties['name'] == hba2_in_props['name']][0]

        self.assertEqual(new_hba.properties, hba2.properties)
        self.assertEqual(new_hba.manager, hba2.manager)

        hba2_out_props = hba2_in_props.copy()
        hba2_out_props.update({
            'element-id': hba2.oid,
            'element-uri': hba2.uri,
        })
        self.assertIsInstance(hba2, FakedHba)
        self.assertEqual(hba2.properties, hba2_out_props)
        self.assertEqual(hba2.manager, partition1.hbas)

    def test_hbas_remove(self):
        """Test remove() of FakedHbaManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        partitions = cpc1.partitions.list()
        partition1 = partitions[0]
        hbas = partition1.hbas.list()
        hba1 = hbas[0]
        self.assertEqual(len(hbas), 1)

        # the function to be tested:
        partition1.hbas.remove(hba1.oid)

        hbas = partition1.hbas.list()
        self.assertEqual(len(hbas), 0)

    # TODO: Add testcases for updating 'hba-uris' parent property


class FakedLparTests(unittest.TestCase):
    """All tests for the FakedLparManager and FakedLpar classes."""

    def setUp(self):
        self.hmc = FakedHmc('fake-hmc', '2.13.1', '1.8')
        self.cpc1_in_props = {'name': 'cpc1'}
        self.lpar1_in_props = {'name': 'lpar1'}
        rd = {
            'cpcs': [
                {
                    'properties': self.cpc1_in_props,
                    'lpars': [
                        {'properties': self.lpar1_in_props},
                    ],
                },
            ]
        }
        # This already uses add() of FakedLparManager:
        self.hmc.add_resources(rd)

    def test_lpars_attr(self):
        """Test CPC 'lpars' attribute."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]

        self.assertIsInstance(cpc1.lpars, FakedLparManager)
        self.assertRegexpMatches(cpc1.lpars.base_uri,
                                 r'/api/logical-partitions')

    def test_lpars_list(self):
        """Test list() of FakedLparManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]

        # the function to be tested:
        lpars = cpc1.lpars.list()

        self.assertEqual(len(lpars), 1)
        lpar1 = lpars[0]
        lpar1_out_props = self.lpar1_in_props.copy()
        lpar1_out_props.update({
            'object-id': lpar1.oid,
            'object-uri': lpar1.uri,
            'status': 'not-activated',
        })
        self.assertIsInstance(lpar1, FakedLpar)
        self.assertEqual(lpar1.properties, lpar1_out_props)
        self.assertEqual(lpar1.manager, cpc1.lpars)

    def test_lpars_add(self):
        """Test add() of FakedLparManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        lpars = cpc1.lpars.list()
        self.assertEqual(len(lpars), 1)

        lpar2_in_props = {'name': 'lpar2'}

        # the function to be tested:
        new_lpar = cpc1.lpars.add(
            lpar2_in_props)

        lpars = cpc1.lpars.list()
        self.assertEqual(len(lpars), 2)

        lpar2 = [p for p in lpars
                 if p.properties['name'] == lpar2_in_props['name']][0]

        self.assertEqual(new_lpar.properties, lpar2.properties)
        self.assertEqual(new_lpar.manager, lpar2.manager)

        lpar2_out_props = lpar2_in_props.copy()
        lpar2_out_props.update({
            'object-id': lpar2.oid,
            'object-uri': lpar2.uri,
            'status': 'not-activated',
        })
        self.assertIsInstance(lpar2, FakedLpar)
        self.assertEqual(lpar2.properties, lpar2_out_props)
        self.assertEqual(lpar2.manager, cpc1.lpars)

    def test_lpars_remove(self):
        """Test remove() of FakedLparManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        lpars = cpc1.lpars.list()
        lpar1 = lpars[0]
        self.assertEqual(len(lpars), 1)

        # the function to be tested:
        cpc1.lpars.remove(lpar1.oid)

        lpars = cpc1.lpars.list()
        self.assertEqual(len(lpars), 0)


class FakedNicTests(unittest.TestCase):
    """All tests for the FakedNicManager and FakedNic classes."""

    def setUp(self):
        self.hmc = FakedHmc('fake-hmc', '2.13.1', '1.8')
        self.cpc1_in_props = {'name': 'cpc1'}
        self.partition1_in_props = {'name': 'partition1'}
        self.nic1_in_props = {
            'name': 'nic1',
            'network-adapter-port-uri': '/api/adapters/1/network-ports/1',
        }
        self.adapter1_in_props = {
            'object-id': '1',
            'name': 'roce1',
            'type': 'roce',
        }
        self.port1_in_props = {
            'element-id': '1',
            'name': 'port1',
        }
        rd = {
            'cpcs': [
                {
                    'properties': self.cpc1_in_props,
                    'partitions': [
                        {
                            'properties': self.partition1_in_props,
                            'nics': [
                                {'properties': self.nic1_in_props},
                            ],
                        },
                    ],
                    'adapters': [
                        {
                            'properties': self.adapter1_in_props,
                            'ports': [
                                {'properties': self.port1_in_props},
                            ],
                        },
                    ],
                },
            ]
        }
        # This already uses add() of FakedNicManager:
        self.hmc.add_resources(rd)

    def test_nics_attr(self):
        """Test Partition 'nics' attribute."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        partitions = cpc1.partitions.list()
        partition1 = partitions[0]

        self.assertIsInstance(partition1.nics, FakedNicManager)
        self.assertRegexpMatches(partition1.nics.base_uri,
                                 r'/api/partitions/[^/]+/nics')

    def test_nics_list(self):
        """Test list() of FakedNicManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        partitions = cpc1.partitions.list()
        partition1 = partitions[0]

        # the function to be tested:
        nics = partition1.nics.list()

        self.assertEqual(len(nics), 1)
        nic1 = nics[0]
        nic1_out_props = self.nic1_in_props.copy()
        nic1_out_props.update({
            'element-id': nic1.oid,
            'element-uri': nic1.uri,
            'device-number': nic1.properties['device-number'],
        })
        self.assertIsInstance(nic1, FakedNic)
        self.assertEqual(nic1.properties, nic1_out_props)
        self.assertEqual(nic1.manager, partition1.nics)

    def test_nics_add(self):
        """Test add() of FakedNicManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        partitions = cpc1.partitions.list()
        partition1 = partitions[0]
        nics = partition1.nics.list()
        self.assertEqual(len(nics), 1)

        nic2_in_props = {
            'name': 'nic2',
            'network-adapter-port-uri': '/api/adapters/1/network-ports/1',
        }

        # the function to be tested:
        new_nic = partition1.nics.add(
            nic2_in_props)

        nics = partition1.nics.list()
        self.assertEqual(len(nics), 2)

        nic2 = [nic for nic in nics
                if nic.properties['name'] == nic2_in_props['name']][0]

        self.assertEqual(new_nic.properties, nic2.properties)
        self.assertEqual(new_nic.manager, nic2.manager)

        nic2_out_props = nic2_in_props.copy()
        nic2_out_props.update({
            'element-id': nic2.oid,
            'element-uri': nic2.uri,
            'device-number': nic2.properties['device-number'],
        })
        self.assertIsInstance(nic2, FakedNic)
        self.assertEqual(nic2.properties, nic2_out_props)
        self.assertEqual(nic2.manager, partition1.nics)

    def test_nics_remove(self):
        """Test remove() of FakedNicManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        partitions = cpc1.partitions.list()
        partition1 = partitions[0]
        nics = partition1.nics.list()
        nic1 = nics[0]
        self.assertEqual(len(nics), 1)

        # the function to be tested:
        partition1.nics.remove(nic1.oid)

        nics = partition1.nics.list()
        self.assertEqual(len(nics), 0)

    # TODO: Add testcases for updating 'nic-uris' parent property


class FakedPartitionTests(unittest.TestCase):
    """All tests for the FakedPartitionManager and FakedPartition classes."""

    def setUp(self):
        self.hmc = FakedHmc('fake-hmc', '2.13.1', '1.8')
        self.cpc1_in_props = {'name': 'cpc1'}
        self.partition1_in_props = {'name': 'partition1'}
        rd = {
            'cpcs': [
                {
                    'properties': self.cpc1_in_props,
                    'partitions': [
                        {'properties': self.partition1_in_props},
                    ],
                },
            ]
        }
        # This already uses add() of FakedPartitionManager:
        self.hmc.add_resources(rd)

    def test_partitions_attr(self):
        """Test CPC 'partitions' attribute."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]

        self.assertIsInstance(cpc1.partitions, FakedPartitionManager)
        self.assertRegexpMatches(cpc1.partitions.base_uri, r'/api/partitions')

    def test_partitions_list(self):
        """Test list() of FakedPartitionManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]

        # the function to be tested:
        partitions = cpc1.partitions.list()

        self.assertEqual(len(partitions), 1)
        partition1 = partitions[0]
        partition1_out_props = self.partition1_in_props.copy()
        partition1_out_props.update({
            'object-id': partition1.oid,
            'object-uri': partition1.uri,
            'status': 'stopped',
            'hba-uris': [],
            'nic-uris': [],
            'virtual-function-uris': [],
        })
        self.assertIsInstance(partition1, FakedPartition)
        self.assertEqual(partition1.properties, partition1_out_props)
        self.assertEqual(partition1.manager, cpc1.partitions)

    def test_partitions_add(self):
        """Test add() of FakedPartitionManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        partitions = cpc1.partitions.list()
        self.assertEqual(len(partitions), 1)

        partition2_in_props = {'name': 'partition2'}

        # the function to be tested:
        new_partition = cpc1.partitions.add(
            partition2_in_props)

        partitions = cpc1.partitions.list()
        self.assertEqual(len(partitions), 2)

        partition2 = [p for p in partitions
                      if p.properties['name'] ==
                      partition2_in_props['name']][0]

        self.assertEqual(new_partition.properties, partition2.properties)
        self.assertEqual(new_partition.manager, partition2.manager)

        partition2_out_props = partition2_in_props.copy()
        partition2_out_props.update({
            'object-id': partition2.oid,
            'object-uri': partition2.uri,
            'status': 'stopped',
            'hba-uris': [],
            'nic-uris': [],
            'virtual-function-uris': [],
        })
        self.assertIsInstance(partition2, FakedPartition)
        self.assertEqual(partition2.properties, partition2_out_props)
        self.assertEqual(partition2.manager, cpc1.partitions)

    def test_partitions_remove(self):
        """Test remove() of FakedPartitionManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        partitions = cpc1.partitions.list()
        partition1 = partitions[0]
        self.assertEqual(len(partitions), 1)

        # the function to be tested:
        cpc1.partitions.remove(partition1.oid)

        partitions = cpc1.partitions.list()
        self.assertEqual(len(partitions), 0)


class FakedPortTests(unittest.TestCase):
    """All tests for the FakedPortManager and FakedPort classes."""

    def setUp(self):
        self.hmc = FakedHmc('fake-hmc', '2.13.1', '1.8')
        self.cpc1_in_props = {'name': 'cpc1'}
        self.adapter1_in_props = {'name': 'adapter1', 'adapter-family': 'osa'}
        self.port1_in_props = {'name': 'port1'}
        rd = {
            'cpcs': [
                {
                    'properties': self.cpc1_in_props,
                    'adapters': [
                        {
                            'properties': self.adapter1_in_props,
                            'ports': [
                                {'properties': self.port1_in_props},
                            ],
                        },
                    ],
                },
            ]
        }
        # This already uses add() of FakedPortManager:
        self.hmc.add_resources(rd)

    def test_ports_attr(self):
        """Test Adapter 'ports' attribute."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        adapters = cpc1.adapters.list()
        adapter1 = adapters[0]

        self.assertIsInstance(adapter1.ports, FakedPortManager)
        self.assertRegexpMatches(adapter1.ports.base_uri,
                                 r'/api/adapters/[^/]+/network-ports')

    def test_ports_list(self):
        """Test list() of FakedPortManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        adapters = cpc1.adapters.list()
        adapter1 = adapters[0]

        # the function to be tested:
        ports = adapter1.ports.list()

        self.assertEqual(len(ports), 1)
        port1 = ports[0]
        port1_out_props = self.port1_in_props.copy()
        port1_out_props.update({
            'element-id': port1.oid,
            'element-uri': port1.uri,
        })
        self.assertIsInstance(port1, FakedPort)
        self.assertEqual(port1.properties, port1_out_props)
        self.assertEqual(port1.manager, adapter1.ports)

    def test_ports_add(self):
        """Test add() of FakedPortManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        adapters = cpc1.adapters.list()
        adapter1 = adapters[0]
        ports = adapter1.ports.list()
        self.assertEqual(len(ports), 1)

        port2_in_props = {'name': 'port2'}

        # the function to be tested:
        new_port = adapter1.ports.add(
            port2_in_props)

        ports = adapter1.ports.list()
        self.assertEqual(len(ports), 2)

        port2 = [p for p in ports
                 if p.properties['name'] == port2_in_props['name']][0]

        self.assertEqual(new_port.properties, port2.properties)
        self.assertEqual(new_port.manager, port2.manager)

        port2_out_props = port2_in_props.copy()
        port2_out_props.update({
            'element-id': port2.oid,
            'element-uri': port2.uri,
        })
        self.assertIsInstance(port2, FakedPort)
        self.assertEqual(port2.properties, port2_out_props)
        self.assertEqual(port2.manager, adapter1.ports)

    def test_ports_remove(self):
        """Test remove() of FakedPortManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        adapters = cpc1.adapters.list()
        adapter1 = adapters[0]
        ports = adapter1.ports.list()
        port1 = ports[0]
        self.assertEqual(len(ports), 1)

        # the function to be tested:
        adapter1.ports.remove(port1.oid)

        ports = adapter1.ports.list()
        self.assertEqual(len(ports), 0)

    # TODO: Add testcases for updating 'network-port-uris' and
    #       'storage-port-uris' parent properties


class FakedVirtualFunctionTests(unittest.TestCase):
    """All tests for the FakedVirtualFunctionManager and FakedVirtualFunction
    classes."""

    def setUp(self):
        self.hmc = FakedHmc('fake-hmc', '2.13.1', '1.8')
        self.cpc1_in_props = {'name': 'cpc1'}
        self.partition1_in_props = {'name': 'partition1'}
        self.virtual_function1_in_props = {'name': 'virtual_function1'}
        rd = {
            'cpcs': [
                {
                    'properties': self.cpc1_in_props,
                    'partitions': [
                        {
                            'properties': self.partition1_in_props,
                            'virtual_functions': [
                                {'properties':
                                 self.virtual_function1_in_props},
                            ],
                        },
                    ],
                },
            ]
        }
        # This already uses add() of FakedVirtualFunctionManager:
        self.hmc.add_resources(rd)

    def test_virtual_functions_attr(self):
        """Test CPC 'virtual_functions' attribute."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        partitions = cpc1.partitions.list()
        partition1 = partitions[0]

        self.assertIsInstance(partition1.virtual_functions,
                              FakedVirtualFunctionManager)
        self.assertRegexpMatches(partition1.virtual_functions.base_uri,
                                 r'/api/partitions/[^/]+/virtual-functions')

    def test_virtual_functions_list(self):
        """Test list() of FakedVirtualFunctionManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        partitions = cpc1.partitions.list()
        partition1 = partitions[0]

        # the function to be tested:
        virtual_functions = partition1.virtual_functions.list()

        self.assertEqual(len(virtual_functions), 1)
        virtual_function1 = virtual_functions[0]
        virtual_function1_out_props = self.virtual_function1_in_props.copy()
        virtual_function1_out_props.update({
            'element-id': virtual_function1.oid,
            'element-uri': virtual_function1.uri,
            'device-number': virtual_function1.properties['device-number'],
        })
        self.assertIsInstance(virtual_function1, FakedVirtualFunction)
        self.assertEqual(virtual_function1.properties,
                         virtual_function1_out_props)
        self.assertEqual(virtual_function1.manager,
                         partition1.virtual_functions)

    def test_virtual_functions_add(self):
        """Test add() of FakedVirtualFunctionManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        partitions = cpc1.partitions.list()
        partition1 = partitions[0]
        virtual_functions = partition1.virtual_functions.list()
        self.assertEqual(len(virtual_functions), 1)

        virtual_function2_in_props = {'name': 'virtual_function2'}

        # the function to be tested:
        new_virtual_function = partition1.virtual_functions.add(
            virtual_function2_in_props)

        virtual_functions = partition1.virtual_functions.list()
        self.assertEqual(len(virtual_functions), 2)

        virtual_function2 = [vf for vf in virtual_functions
                             if vf.properties['name'] ==
                             virtual_function2_in_props['name']][0]

        self.assertEqual(new_virtual_function.properties,
                         virtual_function2.properties)
        self.assertEqual(new_virtual_function.manager,
                         virtual_function2.manager)

        virtual_function2_out_props = virtual_function2_in_props.copy()
        virtual_function2_out_props.update({
            'element-id': virtual_function2.oid,
            'element-uri': virtual_function2.uri,
            'device-number': virtual_function2.properties['device-number'],
        })
        self.assertIsInstance(virtual_function2, FakedVirtualFunction)
        self.assertEqual(virtual_function2.properties,
                         virtual_function2_out_props)
        self.assertEqual(virtual_function2.manager,
                         partition1.virtual_functions)

    def test_virtual_functions_remove(self):
        """Test remove() of FakedVirtualFunctionManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        partitions = cpc1.partitions.list()
        partition1 = partitions[0]
        virtual_functions = partition1.virtual_functions.list()
        virtual_function1 = virtual_functions[0]
        self.assertEqual(len(virtual_functions), 1)

        # the function to be tested:
        partition1.virtual_functions.remove(virtual_function1.oid)

        virtual_functions = partition1.virtual_functions.list()
        self.assertEqual(len(virtual_functions), 0)

    # TODO: Add testcases for updating 'virtual-function-uris' parent property


class FakedVirtualSwitchTests(unittest.TestCase):
    """All tests for the FakedVirtualSwitchManager and FakedVirtualSwitch
    classes."""

    def setUp(self):
        self.hmc = FakedHmc('fake-hmc', '2.13.1', '1.8')
        self.cpc1_in_props = {'name': 'cpc1'}
        self.virtual_switch1_in_props = {'name': 'virtual_switch1'}
        rd = {
            'cpcs': [
                {
                    'properties': self.cpc1_in_props,
                    'virtual_switches': [
                        {'properties': self.virtual_switch1_in_props},
                    ],
                },
            ]
        }
        # This already uses add() of FakedVirtualSwitchManager:
        self.hmc.add_resources(rd)

    def test_virtual_switches_attr(self):
        """Test CPC 'virtual_switches' attribute."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]

        self.assertIsInstance(cpc1.virtual_switches, FakedVirtualSwitchManager)
        self.assertRegexpMatches(cpc1.virtual_switches.base_uri,
                                 r'/api/virtual-switches')

    def test_virtual_switches_list(self):
        """Test list() of FakedVirtualSwitchManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]

        # the function to be tested:
        virtual_switches = cpc1.virtual_switches.list()

        self.assertEqual(len(virtual_switches), 1)
        virtual_switch1 = virtual_switches[0]
        virtual_switch1_out_props = self.virtual_switch1_in_props.copy()
        virtual_switch1_out_props.update({
            'object-id': virtual_switch1.oid,
            'object-uri': virtual_switch1.uri,
        })
        self.assertIsInstance(virtual_switch1, FakedVirtualSwitch)
        self.assertEqual(virtual_switch1.properties, virtual_switch1_out_props)
        self.assertEqual(virtual_switch1.manager, cpc1.virtual_switches)

    def test_virtual_switches_add(self):
        """Test add() of FakedVirtualSwitchManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        virtual_switches = cpc1.virtual_switches.list()
        self.assertEqual(len(virtual_switches), 1)

        virtual_switch2_in_props = {'name': 'virtual_switch2'}

        # the function to be tested:
        new_virtual_switch = cpc1.virtual_switches.add(
            virtual_switch2_in_props)

        virtual_switches = cpc1.virtual_switches.list()
        self.assertEqual(len(virtual_switches), 2)

        virtual_switch2 = [p for p in virtual_switches
                           if p.properties['name'] ==
                           virtual_switch2_in_props['name']][0]

        self.assertEqual(new_virtual_switch.properties,
                         virtual_switch2.properties)
        self.assertEqual(new_virtual_switch.manager,
                         virtual_switch2.manager)

        virtual_switch2_out_props = virtual_switch2_in_props.copy()
        virtual_switch2_out_props.update({
            'object-id': virtual_switch2.oid,
            'object-uri': virtual_switch2.uri,
        })
        self.assertIsInstance(virtual_switch2, FakedVirtualSwitch)
        self.assertEqual(virtual_switch2.properties, virtual_switch2_out_props)
        self.assertEqual(virtual_switch2.manager, cpc1.virtual_switches)

    def test_virtual_switches_remove(self):
        """Test remove() of FakedVirtualSwitchManager."""
        cpcs = self.hmc.cpcs.list()
        cpc1 = cpcs[0]
        virtual_switches = cpc1.virtual_switches.list()
        virtual_switch1 = virtual_switches[0]
        self.assertEqual(len(virtual_switches), 1)

        # the function to be tested:
        cpc1.virtual_switches.remove(virtual_switch1.oid)

        virtual_switches = cpc1.virtual_switches.list()
        self.assertEqual(len(virtual_switches), 0)


if __name__ == '__main__':
    unittest.main()