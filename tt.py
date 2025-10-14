import time
import openpyxl
import random
import multiprocessing

def geneCICT(excelname):
    add1 = ["0x5aace79e0f37596b56adff7b10a1e3c2576380510e931e67d4eb237395dad4ec",
            "0x8049e2b517a57750b2af5b65723360e18be2fba455f46cf20f86019c3fead443",
            "0x78459cd6eb7a765ce832412ae996f02d4743d43b50468ac7f7944ad0530eb95d",
            "0xb1482ca495ead7f944ad0530eb95dad4ec5df30c90ff1123df04524a5524efc4",
            "0x4afa36c5f349f7131f1be52d0b86019c3fead443a3be688a5fefc462f460a24c",
            "0x9efcae4603c110a5524efc462f460a3b24cb293d016fa9701072849a2deae1b6",
            "0x51e04cc9b9ca72849a2addeae1b6774943e8c41b43820a45fe8fc4458014e1bc",
            "0x40e05eac1ec42e3abbc37a5ab3e8fc48014e1bc4b9e07e5b993e9f774fe94536"]
    add2 = ["0x36de7028c1849866a4cdb7c77933e9f774fe9691cd3187eb29924df2be2d0f71",
            "0x18509937debc0fcd363519f700071924df2be2d0f719b407ec76d4a6ccec76d4",
            "0xbfd0364fc63c2355e597dd4ebf7fcf33ffd376d4a6cc9c11b2e6e4d4cafc8a51",
            "0x0bedf4f634ac3f482e54fe6665296efc1fe6e4d4cafc8a51f3f237a94c7b397e",
            "0x3e25960a79dbc69b674cd4ec67a72c62a6c8e2100b5a7e3fa7f237a94c7b397e"]

    workbook=openpyxl.Workbook()
    sheet=workbook.active
    sheet['A1']="id"
    sheet['B1']="from"
    sheet['C1']="to"
    sheet['D1']="data"
    sheet['E1']="timestamp"
    sheet['F1']="runningtime"
    sheet['G1']="start_time"
    sheet['H1']="finish_time"
    sheet['I1']="result"
    for i in range(2,100002):
        fromi=random.randint(0,7)
        toi=random.randint(0,4)
        data=random.randint(0,999983)
        timestamp=int(time.time())
        start_time=time.time()
        temp=data
        for j in range(0,100000):
            temp=(temp*temp)%999983
        finish_time=time.time()
        result=temp
        runningtime=finish_time-start_time
        sheet.append([i,add1[fromi],add2[toi],data,timestamp,runningtime,start_time,finish_time,result])
        print(i)
    workbook.save(excelname)

def geneRWICT(excelname):
    add1 = ["0x5aace79e0f37596b56adff7b10a1e3c2576380510e931e67d4eb237395dad4ec",
            "0x8049e2b517a57750b2af5b65723360e18be2fba455f46cf20f86019c3fead443",
            "0x78459cd6eb7a765ce832412ae996f02d4743d43b50468ac7f7944ad0530eb95d",
            "0xb1482ca495ead7f944ad0530eb95dad4ec5df30c90ff1123df04524a5524efc4",
            "0x4afa36c5f349f7131f1be52d0b86019c3fead443a3be688a5fefc462f460a24c",
            "0x9efcae4603c110a5524efc462f460a3b24cb293d016fa9701072849a2deae1b6",
            "0x51e04cc9b9ca72849a2addeae1b6774943e8c41b43820a45fe8fc4458014e1bc",
            "0x40e05eac1ec42e3abbc37a5ab3e8fc48014e1bc4b9e07e5b993e9f774fe94536"]
    add2 = ["0x36de7028c1849866a4cdb7c77933e9f774fe9691cd3187eb29924df2be2d0f71",
            "0x18509937debc0fcd363519f700071924df2be2d0f719b407ec76d4a6ccec76d4",
            "0xbfd0364fc63c2355e597dd4ebf7fcf33ffd376d4a6cc9c11b2e6e4d4cafc8a51",
            "0x0bedf4f634ac3f482e54fe6665296efc1fe6e4d4cafc8a51f3f237a94c7b397e",
            "0x3e25960a79dbc69b674cd4ec67a72c62a6c8e2100b5a7e3fa7f237a94c7b397e"]

    workbook=openpyxl.Workbook()
    sheet=workbook.active
    sheet['A1']="id"
    sheet['B1']="from"
    sheet['C1']="to"
    sheet['D1']="data"
    sheet['E1']="timestamp"
    sheet['F1']="runningtime"
    sheet['G1']="start_time"
    sheet['H1']="finish_time"
    sheet['I1']="result"
    for i in range(2,100000):
        fromi=random.randint(0,7)
        toi=random.randint(0,4)
        data=""
        timestamp=int(time.time())
        start_time=time.time()
        for j in range(0,100000):
            if add1[0] != "0x5aace79e0f37596b56adff7b10a1e3c2576380510e931e67d4eb237395dad4ec":
                continue
            if add1[1] != "0x5aace79e0f37596b56adff7b10a1e3c2576380510e931e67d4eb237395dad4ec":
                continue
            if add1[2] != "0x5aace79e0f37596b56adff7b10a1e3c2576380510e931e67d4eb237395dad4ec":
                continue
            if add1[3] != "0x5aace79e0f37596b56adff7b10a1e3c2576380510e931e67d4eb237395dad4ec":
                continue
            if add1[4] != "0x5aace79e0f37596b56adff7b10a1e3c2576380510e931e67d4eb237395dad4ec":
                continue
        finish_time=time.time()
        result="True"
        runningtime=finish_time-start_time
        sheet.append([i,add1[fromi],add2[toi],data,timestamp,runningtime,start_time,finish_time,result])
        print(i)
    workbook.save(excelname)


if __name__ == "__main__":
    # with multiprocessing.Pool(processes=10) as pool:
    #     pool.apply_async(geneCICT,("CICT000000.xlsx",))
    #     pool.apply_async(geneCICT,("CICT100000.xlsx",))
    #     pool.apply_async(geneCICT,("CICT200000.xlsx",))
    #     pool.apply_async(geneCICT,("CICT300000.xlsx",))
    #     pool.apply_async(geneCICT,("CICT400000.xlsx",))
    #     pool.apply_async(geneCICT,("CICT500000.xlsx",))
    #     pool.apply_async(geneCICT,("CICT600000.xlsx",))
    #     pool.apply_async(geneCICT,("CICT700000.xlsx",))
    #     pool.apply_async(geneCICT,("CICT800000.xlsx",))
    #     pool.apply_async(geneCICT,("CICT900000.xlsx",))
    #     pool.close()
    #     pool.join()
    # geneRWICT("RWICT000000.xlsx")
    with multiprocessing.Pool(processes=10) as pool:
        pool.apply_async(geneRWICT,("RWICT000000.xlsx",))
        pool.apply_async(geneRWICT,("RWICT100000.xlsx",))
        pool.apply_async(geneRWICT,("RWICT200000.xlsx",))
        pool.apply_async(geneRWICT,("RWICT300000.xlsx",))
        pool.apply_async(geneRWICT,("RWICT400000.xlsx",))
        pool.apply_async(geneRWICT,("RWICT500000.xlsx",))
        pool.apply_async(geneRWICT,("RWICT600000.xlsx",))
        pool.apply_async(geneRWICT,("RWICT700000.xlsx",))
        pool.apply_async(geneRWICT,("RWICT800000.xlsx",))
        pool.apply_async(geneRWICT,("RWICT900000.xlsx",))
        pool.close()
        pool.join()

