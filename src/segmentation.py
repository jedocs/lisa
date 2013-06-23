﻿#
# -*- coding: utf-8 -*-
"""
================================================================================
Name:        segmentation
Purpose:     (CZE-ZCU-FAV-KKY) Liver medical project

Author:      Pavel Volkovinsky
Email:		 volkovinsky.pavel@gmail.com

Created:     08.11.2012
Copyright:   (c) Pavel Volkovinsky
================================================================================
"""

# TODO: Podpora "seeds" - vraceni specifickych objektu
# TODO: Bylo by dobre zavest paralelizmus - otazka jak a kde - neda se udelat vsude, casem si to zjistit - urcite pred bakalarskou praci - asi v ramci PRJ5 nebo az mi bude o prazdninach chybet projekt

import unittest
import sys
sys.path.append("../src/")
sys.path.append("../extern/")

import uiThreshold

import numpy
import numpy.matlib
import scipy
import scipy.io
import scipy.misc
import scipy.ndimage

import logging
logger = logging.getLogger(__name__)

import argparse

# Import garbage collector
import gc as garbage

"""
Vessel segmentation z jater.
    input:
        data - CT (nebo MRI) 3D data
        segmentation - zakladni oblast pro segmentaci, oznacena struktura se stejnymi rozmery jako "data",
            kde je oznaceni (label) jako:
                1 jatra,
                -1 zajimava tkan (kosti, ...)
                0 jinde
        threshold - prah
        voxelsizemm - (vektor o hodnote 3) rozmery jednoho voxelu
        inputSigma - pocatecni hodnota pro prahovani
        dilationIterations - pocet operaci dilation nad zakladni oblasti pro segmentaci ("segmantation")
        dilationStructure - struktura pro operaci dilation
        nObj - oznacuje, kolik nejvetsich objektu se ma vyhledat - pokud je rovno 0 (nule), vraci cela data
        getBiggestObjects - moznost, zda se maji vracet nejvetsi objekty nebo ne
        interactivity - nastavi, zda ma nebo nema byt pouzit interaktivni mod upravy dat
        binaryClosingIterations - vstupni binary closing operations
        binaryOpeningIterations - vstupni binary opening operations

    returns:
        filtrovana data
"""
def vesselSegmentation(data, segmentation = -1, threshold = -1, voxelsizemm = [1,1,1], inputSigma = -1,
dilationIterations = 0, dilationStructure = None, nObj = 1, biggestObjects = True,
interactivity = True, binaryClosingIterations = 1, binaryOpeningIterations = 1):

    print('Pripravuji data...')

    voxel = numpy.array(voxelsizemm)

    ## Kalkulace objemove jednotky (voxel) (V = a*b*c).
    voxel1 = voxel[0]#[0]
    voxel2 = voxel[1]#[0]
    voxel3 = voxel[2]#[0]
    voxelV = voxel1 * voxel2 * voxel3

    ## number je zaokrohleny 2x nasobek objemove jednotky na 2 desetinna mista.
    ## number stanovi doporucenou horni hranici parametru gauss. filtru.
    number = (numpy.round((2 * voxelV**(1.0/3.0)), 2))

    ## Operace dilatace (dilation) nad samotnymi jatry ("segmentation").
    if(dilationIterations > 0.0):
        segmentation = scipy.ndimage.binary_dilation(input = segmentation,
            structure = dilationStructure, iterations = dilationIterations)

    ## Ziskani datove oblasti jater (bud pouze jater nebo i jejich okoli - zalezi,
    ## jakym zpusobem bylo nalozeno s operaci dilatace dat).

    preparedData = data * (segmentation == 1)
    del(data)
    del(segmentation)

    ## Nastaveni rozmazani a prahovani dat.
    if(inputSigma == -1):
        inputSigma = number
    if(inputSigma > number):
        inputSigma = number

    """
    print('Nyni si levym tlacitkem (klepnutim nebo tazenim) oznacte specificke oblasti k vraceni')
    import py3DSeedEditor
    pyed = py3DSeedEditor.py3DSeedEditor(preparedData)
    pyed.show()
    seeds = pyed.seeds
    """

    ## Samotne filtrovani.
    uiT = uiThreshold.uiThreshold(preparedData, voxel, threshold,
        interactivity, number, inputSigma, nObj, biggestObjects, binaryClosingIterations,
        binaryOpeningIterations)#, seeds)
    output = uiT.run()
    del(uiT)
    garbage.collect()

    ## Vraceni matice
    return output

    """
    if(dataFiltering == False):
        ## Data vstoupila jiz filtrovana, tudiz neprosly nalezenim nejvetsich objektu.
        return getPriorityObjects(data = output, N = nObj)
    else:
        ## Data vstoupila nefiltrovana, tudiz jiz prosly nalezenim nejvetsich objektu.
        return output
    """

"""
Vraceni N nejvetsich objektu.
    input:
        data - data, ve kterych chceme zachovat pouze nejvetsi objekty
        N - pocet nejvetsich objektu k vraceni

    returns:
        data s nejvetsimi objekty
"""
def getPriorityObjects(data, N, seeds = None):

    ## Oznaceni dat.
    ## labels - oznacena data.
    ## length - pocet rozdilnych oznaceni.
    labels, length = scipy.ndimage.label(data)

    ## Podminka mnozstvi objektu.
    maxN = 250
    if(length > maxN):
        print('Varovani: Existuje prilis mnoho objektu! (' + str(length) + ')')

    ## Nova verze - podpora seeds - jednodussi ( nekdo dostal lepsi napad :-D )
    if True:

       if seeds == None:
          return labels == 1

       else:

          ## zjistit na zaklade matice seeds (1 - levy klik, 2 - pravy klik, 0 - jindy) objekty k vraceni - ty ktere obsahuji jednicky - muze jich byt vic
          # je nutno v "labels" zjistit, jaka cisla (oznaceni) odpovidaji tem, ktere jsou na stejne pozici v "seeds" jako jednicky, pote je vycucnout z labels a vratit
          # treba neco jako:
            # return labels == 42 + labels == 3
          return labels == 1

    ## Stara verze - nejak to uprave nefunguje - problem s cyklem "for label in numpy.nditer(labels)"
    ## Pry trvala dlouho, ale "AMD FX-8350 - 8 Core 4.2GHz" si nestezuje ;-)
    ## Bylo by dobre zavest paralelizmus - otazka jak a kde - neda se udelat vsude
    else:

         #import collections

        ## Soucet oznaceni z dat.
        import time
        tic = time.clock()
        # arrayLabelsSum = numpy.bincount(labels)
        toc = time.clock()-tic
        print "cas ", toc
        #import pdb; pdb.set_trace()

        # je-li pocet labelu vetsi nez empiricky zjistena hodnota
        # uzije se jeden algoritmus, jinak se vyuzije jiny
        if length > 10:
    #  vracime pocty jednotlivych labelu v datech
            arrayLabelsSum = numpy.zeros(length+1, dtype=numpy.uint32)
            for label in numpy.nditer(labels):
                arrayLabelsSum[label] += 1

            arrayLabels = range(0,length + 1)
        else:

            arrayLabelsSum, arrayLabels = areaIndexes(labels, length)

        #datainlist = list(labels.reshape(-1,1))
    #    toc = time.clock()-toc
    #    print "cas 2", toc
        #x = collections.Counter(datainlist)

        #arrayLabels = [elt for elt,count in x.most_common(3)]
        #toc = time.clock()-toc
        #print "cas 2", toc
    #    print 'ar1 ', arrayLabelsSum

        ## Serazeni poli pro vyber nejvetsich objektu.
        ## Pole arrayLabelsSum je serazeno od nejvetsi k nejmensi cetnosti.
        ## Pole arrayLabels odpovida prislusnym oznacenim podle pole arrayLabelsSum.
        arrayLabelsSum, arrayLabels = selectSort(list1 = arrayLabelsSum, list2 = arrayLabels)
    #    print 'ar2', arrayLabels

        ## Osetreni neocekavane situace.
        if(N > len(arrayLabels)):
    ##        print('Pocet nejvetsich objektu k vraceni chcete vetsi nez je oznacenych oblasti!')
    ##        print('Redukuji pocet nejvetsich objektu k vraceni...')
            N = len(arrayLabels)
            return data

        ##for index1 in range(0, len(arrayLabelsSum)):
            ##print(str(arrayLabels[index1]) + " " + str(arrayLabelsSum[index1]))

    ##    return data == 1

        ## Upraveni dat (ziskani N nejvetsich objektu).
        search = N
        if (sys.version_info[0] < 3):
            import copy
            newData = copy.copy(data) # udelat lepe vynulovani (?)
            newData = newData * 0
        else:
            newData = data.copy()
            newData = newData * 0

        for index in range(0, len(arrayLabels)):
            newData -= (labels == arrayLabels[index])
            if(arrayLabels[index] != 0):
                search -= 1
                if search <= 0:
                    break

        ## Uvolneni pameti
        del(labels)
        del(arrayLabels)
        del(arrayLabelsSum)
        garbage.collect()

        return data - newData# - 1

"""
Zjisti cetnosti jednotlivych oznacenych ploch (labeled areas)
    input:
        labels - data s aplikovanymi oznacenimi
        num - pocet pouzitych oznaceni

    returns:
        dve pole - prvni sumy, druhe indexy
"""
def areaIndexes(labels, num):

    arrayLabelsSum = []
    arrayLabels = []
    for index in range(0, num):
        arrayLabels.append(index)
        sumOfLabel = numpy.sum(labels == index)
        arrayLabelsSum.append(sumOfLabel)

    return arrayLabelsSum, arrayLabels

"""
Razeni 2 poli najednou (list) pomoci metody select sort
    input:
        list1 - prvni pole (hlavni pole pro razeni)
        list2 - druhe pole (vedlejsi pole) (kopirujici pozice pro razeni podle hlavniho pole list1)

    returns:
        dve serazena pole - hodnoty se ridi podle prvniho pole, druhe "kopiruje" razeni
"""
def selectSort(list1, list2):

    length = len(list1)
    for index in range(0, length):
        min = index
        for index2 in range(index + 1, length):
            if list1[index2] > list1[min]:
                min = index2
        ## Prohozeni hodnot hlavniho pole
        list1[index], list1[min] = list1[min], list1[index]
        ## Prohozeni hodnot vedlejsiho pole
        list2[index], list2[min] = list2[min], list2[index]

    return list1, list2

"""
class Tests(unittest.TestCase):

    def test_t(self):
        pass

    def setUp(self):
        #Nastavení společných proměnných pro testy
        datashape = [220,115,30]
        self.datashape = datashape
        self.rnddata = np.random.rand(datashape[0], datashape[1], datashape[2])
        self.segmcube = np.zeros(datashape)
        self.segmcube[130:190, 40:90,5:15] = 1

    def test_same_size_input_and_output(self):
        #Funkce testuje stejnost vstupních a výstupních dat
        outputdata = vesselSegmentation(self.rnddata,self.segmcube)
        self.assertEqual(outputdata.shape, self.rnddata.shape)

    def test_different_data_and_segmentation_size(self):
        # Funkce ověřuje vyhození výjimky při různém velikosti vstpních
        # dat a segmentace
        pdb.set_trace();
        self.assertRaises(Exception, vesselSegmentation, (self.rnddata, self.segmcube[2:,:,:]) )
"""

"""
Main
"""
def _main():

    #print('Byl spusten skript.')
    print('Probiha nastavovani...')

    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)

    ch = logging.StreamHandler()
    logging.basicConfig(format='%(message)s')

    formatter = logging.Formatter("%(levelname)-5s [%(module)s:%(funcName)s:%(lineno)d] %(message)s")
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    parser = argparse.ArgumentParser(description='Segment vessels from liver')
    parser.add_argument('-f','--filename', type=str,
            default = 'lena',
            help='*.mat file with variables "data", "segmentation" and "threshod"')
    parser.add_argument('-d', '--debug', action='store_true',
            help='run in debug mode')
    parser.add_argument('-t', '--tests', action='store_true',
            help='run unittest')
    parser.add_argument('-o', '--outputfile', type=str,
        default='output.mat',help='output file name')
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.tests:
        sys.argv[1:]=[]
        unittest.main()


	print('Nacitam vstup...')

    op3D = True

    if args.filename == 'lena':
        mat = scipy.misc.lena()
        op3D = False
    else:
        mat = scipy.io.loadmat(args.filename)
        logger.debug(mat.keys())

    """
    import py3DSeedEditor
    pyed = py3DSeedEditor.py3DSeedEditor(mat['data'], mat['segmentation'])
    pyed.show()
    seeds = pyed.seeds
    for i in seeds:
        if i == 1:
           print 'hell yeah'
    """

    structure = None
    outputTmp = vesselSegmentation(mat['data'], mat['segmentation'], threshold = -1,
        voxelsizemm = mat['voxelsizemm'], inputSigma = 0.15, dilationIterations = 2,
        nObj = 1, biggestObjects = True, interactivity = True, binaryClosingIterations = 5,
        binaryOpeningIterations = 1)

    import inspector
    inspect = inspector.inspector(outputTmp)
    output = inspect.run()
    del(inspect)
    garbage.collect()

    try:
        cislo = input('Chcete ulozit vystup?\n1 jako ano\ncokoliv jineho jako ne\n')
        if(cislo == '1'):
            print('Ukladam vystup...')
            scipy.io.savemat(args.outputfile, {'data':output})
            print('Vystup ulozen.')

    except Exception:
        print('Nastala chyba!')
        raise Exception

    garbage.collect()
    sys.exit()

if __name__ == "__main__":

    _main()





