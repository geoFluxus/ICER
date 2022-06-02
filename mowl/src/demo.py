from owlready2 import *
import types

skos = get_ontology('http://www.w3.org/2004/02/skos/core#').load()
onto = get_ontology('http://www.exaple.org/demo')
onto.imported_ontologies.append(skos)

lst = ['12', '13', '14']
par = ['23']
with onto:
  class Main(Thing):
    pass

  skos.definition[Main] = 'a large definition of some sort'

  class TP1(Main): pass
  class TP2(Main): pass

  class hasRef(DataProperty, FunctionalProperty):
    range = [str]

  class relsTo(TP1 >> TP2, FunctionalProperty): pass

  for l in lst:
    print('before:',type(l), l)
    l = types.new_class(l, (Main,))
    l.hasRef = f'{l.name}_something'
    print('after:',type(l), l)
    print('--'*40)

  chameleon = types.new_class('23', (onto['12'],))
  print(type(chameleon))
  chameleon.hasRef = 'not_a_number'

  var1 = TP1('var1')
  var2 = TP2('var2')
  var1.relsTo = var2

  skos.definition[var1] = 'let us dwelve over this for a second...'

  tripod = types.new_class('23', (onto['12'],))

print(list(onto.classes()))
print(onto['23'].is_a)
print(onto['12'].hasRef)
print([i.hasRef for i in onto['12'].descendants()])

temp = onto.search(is_a=onto['23'])[0].hasRef[0] == 'not_a_number'
print(temp)

print(list(chameleon.is_a))

print(list(onto.relsTo.get_relations()))
print(onto.var1.definition, var1.iri)

print('-'*40)
for cl in skos.properties():
  print(cl.name)

print(type(skos.definition), skos.definition.iri)

onto.save(file = './ontologies/DEMO.owl', format = "rdfxml")