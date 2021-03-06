"""
Bio3graph triplet extractor.

@author: Vid Podpecan <vid.podpecan@ijs.si>
"""


def bio3graph_create_document_from_file(input_dict):
    from triplet_extractor import data_structures as ds
    fn = input_dict['docfile']
    doc = ds.Document()
    doc.loadString(open(fn).read())
    return {'document': doc}


def bio3graph_create_document_from_string(input_dict):
    from triplet_extractor import data_structures as ds
    from unidecode import unidecode

    docstr = input_dict['docstr']
    doc = ds.Document()
    doc.loadString(unidecode(docstr))
    return {'document': doc}


def bio3graph_split_sentences(input_dict):
    from triplet_extractor import data_structures as ds
    doc = input_dict['document']
    ds.SentenceSplitter().splitNLTK(doc)
    return {'document': doc}


def bio3graph_parse_sentences(input_dict):
    from triplet_extractor import data_structures as ds
    doc = input_dict['document']
    if not doc.rawSentences:
        raise TypeError('Input document is not split into sentences! Use splitter first.')
    gtc = ds.GeniaTTC()
    gtc.process(doc)
    return {'document': doc}


def bio3graph_build_vocabulary(input_dict):
    from triplet_extractor import tripletExtraction as te

    voc = te.Vocabulary()
    voc.loadCompounds_file(input_dict['compounds'])
    voc.loadPredicates_files(activationFname=input_dict['activation'],
                             activations_rotate=input_dict['activation_rotate'],
                             inhibitionFname=input_dict['inhibition'],
                             bindingFname=input_dict['binding'],
                             activationFname_passive=input_dict['activation_passive'],
                             inhibitionFname_passive=input_dict['inhibition_passive'],
                             bindingFname_passive=input_dict['binding_passive'])
    return {'vocabulary': voc}


def bio3graph_build_default_vocabulary(input_dict):
    from triplet_extractor import tripletExtraction as te
    from os.path import normpath, join, dirname

    dname = normpath(dirname(__file__))
    voc = te.Vocabulary()
    voc.loadCompounds_file(join(dname, 'triplet_extractor/vocabulary/compounds.lst'))
    voc.loadPredicates_files(activationFname=join(dname, 'triplet_extractor/vocabulary/activation.lst'),
                             activations_rotate=join(dname, 'triplet_extractor/vocabulary/activation_rotate.lst'),
                             inhibitionFname=join(dname, 'triplet_extractor/vocabulary/inhibition.lst'),
                             bindingFname=join(dname, 'triplet_extractor/vocabulary/binding.lst'),
                             activationFname_passive=join(dname, 'triplet_extractor/vocabulary/activation_pas.lst'),
                             inhibitionFname_passive=join(dname, 'triplet_extractor/vocabulary/inhibition_pas.lst'),
                             bindingFname_passive=join(dname, 'triplet_extractor/vocabulary/binding_pas.lst'))
    return {'vocabulary': voc}


def bio3graph_build_default_vocabulary_custom_compounds(input_dict):
    from triplet_extractor import tripletExtraction as te
    from os.path import normpath, join, dirname
    from StringIO import StringIO

    comp = input_dict['compounds']

    dname = normpath(dirname(__file__))
    voc = te.Vocabulary()
    s = StringIO()
    s.write(comp)
    s.flush()
    voc.loadCompounds_file(s)
    voc.loadPredicates_files(activationFname=join(dname, 'triplet_extractor/vocabulary/activation.lst'),
                             activations_rotate=join(dname, 'triplet_extractor/vocabulary/activation_rotate.lst'),
                             inhibitionFname=join(dname, 'triplet_extractor/vocabulary/inhibition.lst'),
                             bindingFname=join(dname, 'triplet_extractor/vocabulary/binding.lst'),
                             activationFname_passive=join(dname, 'triplet_extractor/vocabulary/activation_pas.lst'),
                             inhibitionFname_passive=join(dname, 'triplet_extractor/vocabulary/inhibition_pas.lst'),
                             bindingFname_passive=join(dname, 'triplet_extractor/vocabulary/binding_pas.lst'))
    return {'vocabulary': voc}


def bio3graph_extract_triplets(input_dict):
    from triplet_extractor import tripletExtraction as te
    voc = input_dict['vocabulary']
    doc = input_dict['document']

    ex = te.TripletExtractor(voc)
    triplets = ex.extractTripletsNLP(doc, VP_CHECK_POS=1)
    return {'triplets': triplets}


def bio3graph_normalise_triplets(input_dict):
    from triplet_extractor import tripletExtraction as te
    triplets = input_dict['triplets']
    voc = input_dict['vocabulary']
    ex = te.TripletExtractor(voc)
    normalised = ex.normalizeTriplets(triplets)
    return {'normalised_triplets': normalised}


def bio3graph_construct_triplet_network(input_dict):
    from triplet_extractor import tripletExtraction as te
    triplets = input_dict['triplets']
    gk = te.TripletGraphConstructor(triplets)
    graph = gk.export_networkx()
    return {'network_object': graph}


def bio3graph_export_triplets_to_text(input_dict):
    from triplet_extractor import tripletExtraction as te
    triplets = input_dict['triplets']
    gk = te.TripletGraphConstructor(triplets)
    ttext = gk.exportText()
    return {'triplets_as_text': ttext}


def bio3graph_networkx_to_biomine(input_dict):
    from triplet_extractor import graph_operations as gop
    nwx = input_dict['network']
    bmg = gop.export_to_BMG(nwx)
    return {'biomine_graph': bmg}


def bio3graph_biomine_to_networkx(input_dict):
    from triplet_extractor import graph_operations as gop
    bmg = input_dict['biomine_graph']
    nwx = gop.load_BMG_to_networkx(bmg)
    return {'network_object': nwx}


def bio3graph_biomine_visualizer(input_dict):
    return {'biomine_graph': input_dict.get('biomine_graph', None)}


def bio3graph_find_redundant_transitive_relations(input_dict):
    from triplet_extractor import graph_operations as gop
    initialNetwork = input_dict['initial_network']
    newNetwork = input_dict['new_network']
    result = gop.find_transitive_relations(initialNetwork, newNetwork)
    return {'transitive_relations': result}


def bio3graph_remove_relations(input_dict):
    from networkx import copy

    nwx = copy.deepcopy(input_dict['network'])
    relations = input_dict['relations']
    for (fr, to, relType) in relations:
        if nwx.has_edge(fr, to, relType):
            nwx.remove_edge(fr, to, relType)
    return {'pruned_graph': nwx}


def bio3graph_incremental_network_merge(input_dict):
    from triplet_extractor import graph_operations as gop

    old = input_dict['existing_network']
    new = input_dict['new_network']
    merged = gop.merge_incremental_graph(old,new)
    return {'merged_network': merged}


def bio3graph_colour_relations(input_dict):
    from triplet_extractor import graph_operations as gop
    from networkx import copy

    nwx = copy.deepcopy(input_dict['network'])
    rels = input_dict['relations']
    gop.colour_relations(nwx, rels)
    return {'network': nwx}


def bio3graph_reset_colours(input_dict):
    from triplet_extractor import graph_operations as gop
    from networkx import copy

    nwx = copy.deepcopy(input_dict['network'])
    gop.reset_edge_colors(nwx)
    return {'network': nwx}


def bio3graph_search_pubmed(input_dict):
    from NCBI import NCBI_Extractor

    q = input_dict['query']
    if not q:
        raise ValueError('Empty PubMed query!')

    nhits = input_dict['maxHits']
    maxHits = int(nhits) if nhits else 0

    ex = NCBI_Extractor()
    ids = ex.query(q, maxHits=maxHits)
    return {'pmids': ids}


def bio3graph_filter_open_access(input_dict):
    import cPickle
    from os.path import normpath, join, dirname

    oa = cPickle.load(open(normpath(join(dirname(__file__), 'data/OA_dict.pickle')), 'rb'))
    ids = input_dict['ids']
    result = filter(lambda(x): True if x in oa else False, ids)
    return {'oa_ids': result}


def bio3graph_get_xmls(input_dict):
    from NCBI import NCBI_Extractor

    ids = input_dict['id_list']
    if not isinstance(ids, list):
        ids = list(ids)

    result = []
    a = NCBI_Extractor()
    for did in ids:
        result.append(a.getXML(did))
    return {'xmls': result}

def bio3graph_get_fulltexts(input_dict):
    from NCBI import NCBI_Extractor

    ids = input_dict['id_list']
    if not isinstance(ids, list):
        ids = list(ids)

    result = []
    a = NCBI_Extractor()
    for did in ids:
        doc = a.getFulltext(did)
        ft = '%s\n%s\n%s\n' % (doc.title, doc.abstract, doc.body)
        result.append(ft)
    return {'fulltexts': result}


def bio3graph_xml_to_fulltext(input_dict):


    return {}

def bio3graph_xml_to_fulltext_finished(postdata, input_dict, output_dict):
    file_name = input_dict['xml_file']
    output_file_name=file_name+".new"
    #if not isinstance(xmls, list):
    #    xmls = [xmls]

    num_of_all_articles=postdata.get('num_of_all_articles')[0]
    article_count=0
    from NCBI import NCBI_Extractor
    a = NCBI_Extractor()

    widget_id = postdata.get('widget_id')[0]
    sections = postdata.get('section_names%s' % widget_id)
    sections=[s.replace("figure captions","fig").replace("table captions","table-wrap").replace("article title","title-group").split("::")[0] for s in sections]

    def get_title(elem):
        txt=''
        if elem.text:
            txt+=elem.text.strip()
        for child in elem._children: #only one level
            if child.text:
                txt+=child.text.strip()
            if child.tail:
                txt+=child.tail.strip()
        if elem.tail:
            txt+=elem.tail.strip()
        return txt.lower()

    def write_to_results(elem_tag,text,results,path,write_from_level,block_from_level):
        if len(path)>=write_from_level and not len(path)>=block_from_level:
            if text and text.replace('\n', '').strip()!="":
                results.append(text.replace('\n', ''))
                if not elem_tag in ['bold','underline','italic','sub','sup']:
                    results.append(" ")
        return None

    import xml.etree.ElementTree as ET
    import re

    def writing_element(elem,sections):
        if elem.tag=='sec':
            return 'sec-type' in elem.attrib and elem.attrib['sec-type'] in sections
        else:
            return elem.tag in sections

    results=[]
    skipTags=['title','xref', 'table', 'graphic', 'ext-link', 'media', 'inline-formula', 'disp-formula','label']
    with open(file_name) as f:
        with open(output_file_name,"w") as output_file:
    #with open("D:/diagonalization/glio_aml/domain1/1062151.xml") as f:
            path=[]
            tails=[]
            write_from_level=100
            block_from_level=100
            for event, elem in ET.iterparse(f,events=("start","end")):
                if event=="start":
                    path.append(elem.tag)
                    tails.append(elem.tail)
                    #ancestors.add(elem)
                    if elem.tag == "article":
                        write_from_level=100
                        block_from_level=100
                    else:
                        if elem.tag in skipTags:
                            block_from_level=min([block_from_level,len(path)])
                        if elem.tag=='sec' and 'sec-type' in elem.attrib and elem.attrib['sec-type'] in sections:
                            write_from_level=min([len(path)+1,write_from_level])
                        elif elem.tag in sections: #abstract
                            write_from_level=min([len(path),write_from_level])
                        elif elem.tag=="title" and get_title(elem) in sections:
                            write_from_level=min([len(path)-1,write_from_level])
                    if elem.tag=="underline":
                        stop=True
                    #res=""
                    write_to_results(elem.tag,elem.text,results,path,write_from_level,block_from_level)

                elif event=="end":
                    tail=tails.pop()
                    path.pop()

                    write_to_results(elem.tag,tail,results,path,write_from_level,block_from_level)

                    if len(path)<write_from_level:
                        write_from_level=100
                    if len(path)<block_from_level:
                        block_from_level=100
                    if elem.tag=="article":
                        body = ''.join(results) #
                        #a.list2text(results)
                        body = re.sub('(\[)[ ,-:;]*(\])', '', body)
                        body=body.replace("  "," ").replace(" ( )","").replace(" .",".").replace(" ,",",")+"\n"
                        output_file.write(body)
                        results=[]
                        article_count+=1
                        print article_count,"/",num_of_all_articles
                elem.clear()


    return {'output_file' : output_file_name}


def bio3graph_map_entrez_to_ncbi_symbol(input_dict):
    import cPickle
    from os.path import normpath, join, dirname

    e2symb = cPickle.load(open(normpath(join(dirname(__file__), 'data/entrez2symbol.pickle')), 'rb'))
    glist = input_dict['genes']
    result = []
    for g in glist:
        g = g.replace('EntrezGene:', '')
        g = int(g)
        symb = e2symb.get(g)
        if symb:
            result.append(symb)
    return {'gene_symbols': result}


def bio3graph_get_gene_synonyms_from_GPSDB(input_dict):
    from GPSDB_synonyms import Synonym_extractor

    glist = input_dict['gene_symbols']
    a = Synonym_extractor()
    result = a.get_geneset_synonyms(glist)
    return {'gene_synonyms': result}


def bio3graph_construct_compounds_from_gene_synonyms(input_dict):
    import csv
    from StringIO import StringIO

    syns = input_dict['gene_synonyms']
    s = StringIO()
    w = csv.writer(s)
    for g in syns:
        elts = [g] + syns[g]
        w.writerow(elts)
    s.flush()
    result = s.getvalue()
    return {'compounds_csv': result}



def mesh_filter(input_dict):
    return {'output_file':'svoboden kot pticek na veji'}

def mesh_filter_finished(postdata, input_dict, output_dict):
    import cPickle
    from os.path import normpath, join, dirname

    widget_id = postdata.get('widget_id')[0]
    selected_categories=postdata.get('selected[]')
    terms_per_category=cPickle.load(open(normpath(join(dirname(__file__),'data/terms_per_category.pickle'))))

    terms=set()
    for category in selected_categories:
        if not category in selected_categories:
            print "aaa"
        terms |= terms_per_category[category]

    import time
    unique_filename=time.strftime("%Y-%m-%d-%H-%M-%S")
    output_file_name="C:/Users/matic/workspace/iClowdFlow/mothra/public/files/1/terms_"+str(unique_filename)+".txt"
    with open(output_file_name,'w') as of:
        for term in terms:
            of.write("%s\n" % term)

    return {'output_file':output_file_name}



















