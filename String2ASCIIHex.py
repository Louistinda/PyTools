
SN = ''
while True:
    myStr = input("请输入BPSCheckSN:")
    if len(myStr) == 32:
        for cnt in range(16):
            SN += chr(int(myStr[cnt*2:cnt*2+2], 16))
        print(SN, end="")
        SN = ''
    elif len(myStr) == 16:
        for word in myStr:
            print(str(hex(ord(word)))[2:4], end="")
    else:
        print("输入内容长度错误，请重新输入！", end="")
    print()
