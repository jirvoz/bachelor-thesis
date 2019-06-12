from compat import OrderedDict


# Abstraktni rozhrani adapteru
class Adapter(object):

    def load(self):
        raise NotImplementedError

    def save(self, root_section):
        raise NotImplementedError


class XMLAdapter(Adapter):

    DEFAULT_FILE_NAME = 'store.xml'

    # XPath expressions
    XPATH_ALL_ATTRS = '@*'
    XPATH_ALL_CHILDS = './*'

    def __init__(self, file_name=DEFAULT_FILE_NAME):
        self._file_name = file_name

    def load(self):
        import libxml2
        d = libxml2.parseFile(self._file_name)
        root = d.getRootElement()

        params = root.xpathEval(XMLAdapter.XPATH_ALL_ATTRS)
        params_list = OrderedDict()
        for p in params:
            params_list[p.name] = p.content

        root_section = Section(root.name, params_list)

        # Recursively load all child nodes (and its params)
        # and interpret them as sections
        def load_sections(sec, root_node):
            for child_node in root_node.xpathEval(XMLAdapter.XPATH_ALL_CHILDS):
                params = child_node.xpathEval(XMLAdapter.XPATH_ALL_ATTRS)
                params_list = {}
                for p in params:
                    params_list[p.name] = p.content

                chld_sec = sec.add_sub_section(Section(child_node.name, params_list))
                load_sections(chld_sec, child_node)

        load_sections(root_section, root)
        d.freeDoc()
        return root_section

    def save(self, root_section):
        import libxml2
        d = libxml2.newDoc('1.0')

        root = libxml2.newNode(root_section.get_name())

        def save_sections(sec, root_node):
            for index, val in sec.get_params().iteritems():
                root_node.setProp(index, str(val))

            for subsec in sec:
                chld = libxml2.newNode(subsec.get_name())
                root_node.addChild(chld)
                save_sections(subsec, chld)

        save_sections(root_section, root)

        # Add root section into document
        d.addChild(root)
        d.saveFormatFile(self._file_name, True)
        d.freeDoc()

    def get_xml_filename(self):
        return self._file_name


class SQLAdapter(Adapter):
    def load(self):
        pass

    def save(self, root_section):
        pass


class Section(object):
    def __init__(self, name, params=None):
        self._name = name
        if params is None:
            self._params = OrderedDict()
        else:
            self._params = params
        self._sub_sections = OrderedDict()

    def __getitem__(self, index):
        return self.get_subsections_by_name(index)

    def __repr__(self):
        return 'Section %s (%s)' % (self.get_name(), self._params or '')

    def set_params(self, **params):
        self._params = params

    def get_params(self):
        return self._params

    def get_name(self):
        return self._name

    def add_sub_section(self, sec):
        key = sec.get_name()
        if key not in self._sub_sections:
            self._sub_sections[key] = []

        self._sub_sections[key].append(sec)
        return sec

    def get_subsections_by_name(self, name):
        return self._sub_sections.get(name, [])

    def get_subsections_by_param_val(self, **kwargs):
        ret = []
        for item in self.get_subsections():
            item_match = True
            for k, v in kwargs.iteritems():
                item_params = item.get_params()
                if k in item_params.keys():
                    if item_params[k] != v:
                        item_match = False
            if item_match:
                ret.append(item)
        return ret

    def get_subsections(self):
        for subsec in self._sub_sections.itervalues():
            for sub in subsec:
                yield sub

    def search_section_childs(self, section_name, param_name):
        return self._search_section_params(self, section_name, param_name)

    def _search_section_params(self, section, section_name, param_name):
        param_values = set()
        for s in section.get_subsections():
            if s.get_name() == section_name:
                for key, val in s.get_params().iteritems():
                    if key == param_name:
                        param_values.add(val)
            deeper_values = self._search_section_params(s, section_name, param_name)
            param_values |= deeper_values
        return param_values

    # Generator for subsections
    def __iter__(self):
        return self.get_subsections()


class Document(object):

    def __init__(self, adapter):
        self._adapter = adapter
        self._root_section = None

    def create_root_section(self, sec):
        self._root_section = sec

    def get_root_section(self):
        return self._root_section

    def set_adapter(self, adapter):
        self._adapter = adapter

    def get_adapter(self):
        return self._adapter

    def add_sub_section(self, sec):
        return self._root_section.add_sub_section(sec)

    def save(self):
        self._adapter.save(self._root_section)

    def load(self):
        self._root_section = self._adapter.load()


if __name__ == '__main__':
    #       Saving XML

    # Vytvoreni patricneho adapteru
    ad = XMLAdapter('file.xml')

    # Vytvoreni jakehosi "dokumentu" a jeho 'root' sekce
    doc = Document(ad)
    info_args = OrderedDict([("kernel", '3.10.0-244.el7.x86_64'),
                            ("system_release", 'Red Hat Enterprise Linux Server release 7.1 (Maipo)'),
                            ("hostname", 'ibm-x3650m3-02.lab.eng.brq.redhat.com')
                             ])
    r_section = Section('host', info_args)
    doc.create_root_section(r_section)
    doc.add_sub_section(Section("SanityTest"))
    subsecNetperf = doc.add_sub_section(Section("NetperfTCPStream"))

    # Vytvoreni dvou do sebe vnorenych podsekci
    subsection_1 = OrderedDict([("dstip", '172.18.10.20'),
                                ("AF", 'INET4'),
                                ("dstname", 'bnx2_1'),
                                ("srcname", 'bnx2_1'),
                                ("srcip", '172.18.10.10')
                                ])
    secPath = subsecNetperf.add_sub_section(Section('path', subsection_1))

    subsection_2 = OrderedDict([("buffer_size", "30")
                                ])

    secSettings = secPath.add_sub_section(Section('setting', subsection_2))

    # Vytvoreni sekci na stejne urovni
    for i in range(10):
        s = Section('test')
        s.set_params(rcv_socket_size='87380', service_local='%s' % i, snd_socket_size='%s' % i, loc_util='%s' % i, throughput='%s' % i)
        secSettings.add_sub_section(s)

    doc.save()
    ###########################################

    #       Loading XML
    doc_l = Document(ad)
    doc.load()
    # loaded_root_section = doc.get_root_section()  # Example how to get root section from document

    # Create new adapter and save loaded data to file 'test.xml'.
    ad_new = XMLAdapter('test.xml')
    doc.set_adapter(ad_new)
    doc.save()

    # Files 'file.xml' and 'test.xml' should be the same (structure, names and arguments) - maybe it will not be exactly 1:1 when 'diff' is used -> must be tested with xmllint:
    # $ xmllint --c14n file.xml > 1.xml
    # $ xmllint --c14n test.xml > 2.xml
    # $ diff 1.xml 2.xml

    # Load test
    adXYZ = XMLAdapter('test.xml')
    docXYZ = Document(adXYZ)
    docXYZ.load()

    root_secXYZ = docXYZ.get_root_section()

    assert root_secXYZ.get_name() == 'host'

    # returns generator of subsections
    subs1 = list(root_secXYZ.get_subsections())

    print(root_secXYZ)

    for s in subs1:
        print(s)
        for ss in s:
            print(ss)
            for sss in ss:
                test_subs = list(sss['test'])
                for abc in test_subs:
                    assert abc.get_name() == 'test'

                for ssss in sss:
                    print(ssss)

    ###########################################
