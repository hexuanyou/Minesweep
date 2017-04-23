# minesweep.py
#   A program to sweep the mine in assist mode
#   There is a sweeper mine game if you select the game mode
# By:   He Xuanyou
# Version: 1.0
# Date: 2017-04

from Tkinter import *
import tkMessageBox
import codecs
import sys
import time
import Queue
import random

#defualt mine number setting
div = 4
sub = 1

def searchmine(x, y, flag_mine):
    minenum = 0
    if((flag_mine[x+1][y+1])==0):
        for i in range(3):
            for j in range(3):
                minenum = minenum + flag_mine[x+i][y+j]
    else: minenum = 9
    return minenum

#aro_array_gen
#Generate a new array that val is around the input array
"""
val=0
                    |0 0 0 0 0  ... 0  0|
|a1 a2 a3 ... an|   |0 a1 a2 a3 ... an 0|
|b1 b2 b3 ... bn|   |0 b1 b2 b3 ... bn 0|
|c1 c2 c3 ... cn|   |0 c1 c2 c3 ... cn 0|
                    |0 0 0 0 0  ... 0  0|
    array_a             ar_array
"""
def aro_array_gen(array_a, row, col, val):     
    listd = [val]*col
    ar_array = [[val for i in range(col+2)] for i in range(row+2)]
    array_b = [listd] + array_a + [listd]
    for i in range(row+2):
        ar_array[i] = [val]+array_b[i]+[val]
    return ar_array

def minecounter(array_a, row, col, x, y):
    ar_array = aro_array_gen(array_a, row, col, 0)
    num = searchmine(x, y, ar_array)
    return num

def array_gen(lst, row, col):
    array = [[0 for i in range(col)] for i in range(row)]
    for i in range(row):
        array[i] = lst[i*col:(i+1)*col]
    return array

def inrange(row, col, x, y):
    if(x<0 or x>=row):return 0
    if(y<0 or y>=col):return 0
    return 1


class GUI:
    def __init__(self):
        self.root = Tk()
        self.root.title('Mine Sweepping Assist')
        self.blocksize = [8,8,8,8]    # self.blocksize[row, column, new row, new column]
        sizex = int(125*self.blocksize[1]/4)+30
        sizey = int(122*self.blocksize[0]/4)+30
        self.root.geometry('%dx%d'%(sizex, sizey))
        
        self.frame = Frame(self.root, width=31*self.blocksize[0], height=30*self.blocksize[1])
        
        self.open = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
        self.minelst = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
        self.flag_mine = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
        self.flag_assume = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
        self.open_assume = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
        
        self.frame.place(x=16,y=0)
        self.block()
        self.undo = Queue.LifoQueue()
        self.mineleft = int((self.blocksize[0]*self.blocksize[1])/div - sub)
        self.mineleft_buf = self.mineleft
        self.var = StringVar()
        self.minelabel = Label(self.root, textvariable=self.var, relief=GROOVE, bd=2,
            width=5, bg='darkblue',fg='white')
        self.mine_log = Label(self.root, width=5, height=1, text='@', fg='red')
        self.mine_log.place(x=int(sizex*8/10), y=int(sizey*99/100)-25)
        self.minelabel.place(x=int(sizex*8/10)-40, y=int(sizey*99/100)-25)
        self.var.set('%d'%self.mineleft)
        self.var_pk = StringVar()
        self.pklabel = Label(self.root, textvariable=self.var_pk, width=5)
        self.pklabel.place(x=int(sizex*5/10)-20, y=int(sizey*99/100)-25)

        self.clock = Label(self.root, text="0", relief=GROOVE, bd=2,
            width=5, bg='darkblue',fg='white')
        self.clock.place(x=int(sizex*2/10), y=int(sizey*99/100)-25)
        
        self.mode = 1
        self.game_state = 0
        self.setmenu()

        self.minecolor = ['blue','seagreen','red','navy','brown','darkcyan','firebrick','darkred']

        self.seed = 0
        self.ts = 0
        self.showtime()
        self.pk = [-1, -1, -1, -1, -1, -1, -1, -1]
        self.right_flag = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
        
    def setmenu(self):
        menubar = Menu(self.root)
        ###########
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.reset)
        filemenu.add_command(label="Open", command=self.donothing)
        filemenu.add_command(label="Save", command=self.donothing)
        filemenu.add_command(label="Save as...", command=self.donothing)
        filemenu.add_command(label="Close", command=self.donothing)
        
        filemenu.add_separator()
        
        filemenu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=filemenu)
        ###########
        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=self.undoset)
        
        editmenu.add_separator()
        
        editmenu.add_command(label="Setting", command=self.setmine)
        editmenu.add_command(label="Copy", command=self.donothing)
        editmenu.add_command(label="Paste", command=self.donothing)
        editmenu.add_command(label="Delete", command=self.donothing)
        editmenu.add_command(label="Select All", command=self.donothing)
        
        menubar.add_cascade(label="Edit", menu=editmenu)
        ###########
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help Index", command=self.helpfile)
        helpmenu.add_command(label="About...", command=self.about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        ###########
        modemenu = Menu(menubar, tearoff=0)

        modemenu.add_radiobutton(label="game mode", command=lambda v=1 : self.modemenu(v))
        modemenu.add_radiobutton(label="assist mode", command=lambda v=2 : self.modemenu(v))
        menubar.add_cascade(label="Mode", menu=modemenu)
        self.modemenu(1)
        ###########
        self.root.configure(menu=menubar)
        
    def donothing(self):
        filewin = Toplevel(self.root, height=100, width=300)
        filewin.minsize(300,100)
        filewin.maxsize(300,100)
        filewin.title('nothing')
        button = Button(filewin, text="Do nothing button", command=filewin.destroy)
        button.place(x=90,y=30)
        
    def modemenu(self, value):
        if(value==1 and self.mode != 1):
            self.mode = 1
            self.reset()
        elif(value==2 and self.mode != 2):
            self.mode = 2
            self.reset()
##            self.minenum_inp()
        
    def reset(self):
        for i in range(self.blocksize[0]):
            for j in range(self.blocksize[1]):
                bk = getattr(self, 'b%dk%d'%(i, j))
                if(self.open[i][j]):
                    self.open[i][j] = 0
                    bk.configure(relief=RAISED, state=NORMAL, bd=2, bg='royalblue', text=' ')
                    if(hasattr(self, 'mine_num_ent%d_%d' % (i, j))):
                        ent = getattr(self, 'mine_num_ent%d_%d' % (i, j))
                        ent.destroy()
                    if(hasattr(self, 'mine_num_dsp%d_%d' % (i, j))):
                        dsp = getattr(self, 'mine_num_dsp%d_%d' % (i, j))
                        dsp.destroy()
                bk.configure(bg='royalblue', text=' ')
                self.flag_assume[i][j] = 0
                self.flag_mine[i][j] = 0
                self.minelst[i][j] = 0
                self.open_assume[i][j] = 0
        sizex = int(125*self.blocksize[1]/4)+30
        sizey = int(122*self.blocksize[0]/4)+30
        self.root.geometry('%dx%d'%(sizex, sizey))
        self.game_state = 0
        while not self.undo.empty() : self.undo.get()
        self.mineleft = self.mineleft_buf
        self.var.set('%d'%self.mineleft)
        self.clock.configure(text = "%d"%(0))
        self.ts = 0
        self.pk = [-1, -1, -1, -1, -1, -1, -1, -1]
        if(self.mode == 2):self.magic = Magic(self.blocksize[0:2], self.mineleft)

    def rebuild(self):
        if(self.blocksize[0:2]!=self.blocksize[2:4]):
            for i in range(self.blocksize[0]):
                for j in range(self.blocksize[1]):
                    bk = getattr(self, 'b%dk%d'%(i, j))
                    bk.destroy()
                    if(hasattr(self, 'mine_num_ent%d_%d' % (i, j))):
                        ent = getattr(self, 'mine_num_ent%d_%d' % (i, j))
                        ent.destroy()
                    if(hasattr(self, 'mine_num_dsp%d_%d' % (i, j))):
                        dsp = getattr(self, 'mine_num_dsp%d_%d' % (i, j))
                        dsp.destroy()
            self.blocksize[0:2]=self.blocksize[2:4]
            self.open = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
            self.minelst = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
            self.flag_mine = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
            self.flag_assume = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
            self.open_assume = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
            self.block()
            sizex = int(125*self.blocksize[1]/4)+30
            sizey = int(122*self.blocksize[0]/4)+30
            self.root.geometry('%dx%d'%(sizex, sizey))
            self.minelabel.place(x=int(sizex*8/10)-40, y=int(sizey*99/100)-25)
            self.mine_log.place(x=int(sizex*8/10), y=int(sizey*99/100)-25)
            self.pklabel.place(x=int(sizex*5/10)-20, y=int(sizey*99/100)-25)
            self.clock.place(x=int(sizex*2/10), y=int(sizey*99/100)-25)
            self.clock.configure(text = "%d"%(0))
            self.root.geometry('%dx%d'%(sizex, sizey))
            self.game_state = 0
            while not self.undo.empty() : self.undo.get()
            self.mineleft = self.mineleft_buf
            self.var.set('%d'%self.mineleft)
            self.ts = 0
            self.pk = [-1, -1, -1, -1, -1, -1, -1, -1]
            if(self.mode == 2):self.magic = Magic(self.blocksize[0:2], self.mineleft)
        else:
            self.reset()

    def showtime(self):
        time1 = time.time()
        if(self.ts>0):
            time2 = int(time1 - self.ts)
            if(time2>999):time2=999
            self.clock.configure(text = "%d"%(time2))
        self.clock.after(500, self.showtime)
    
    def showmine(self, gate):
        if(gate):
            for j in range(self.blocksize[1]):
                for i in range(self.blocksize[0]):
                    if(not self.open[i][j] and not self.flag_assume[i][j] and self.flag_mine[i][j]):
                        self.open[i][j] = 1
                        bk = getattr(self, 'b%dk%d'%(i, j))
                        bk.configure(state=NORMAL, bg='lightblue', text='@', fg='red')
                    elif(not self.open[i][j] and self.flag_mine[i][j]):
                        bk = getattr(self, 'b%dk%d'%(i, j))
                        bk.configure(bg = 'lightblue', text='@|>', fg='red')
                    elif(not self.open[i][j] and self.flag_assume[i][j]):
                        bk = getattr(self, 'b%dk%d'%(i, j))
                        bk.configure(bg='royalblue')
        else:
            for j in range(self.blocksize[1]):
                for i in range(self.blocksize[0]):
                    if(self.flag_mine[i][j]):
                        bk = getattr(self, 'b%dk%d'%(i, j))
                        bk.flash()
        
    def setok(self, win):
        win.destroy()
        self.rebuild()
        
    def undoset(self):
        if(not self.undo.empty()):
            pkx = self.undo.get()
            pky = self.undo.get()
            self.open[pkx][pky] = 0
            bk = getattr(self, 'b%dk%d'%(pkx, pky))
            bk.configure(relief=RAISED, state=NORMAL, bd=2, bg='royalblue')
            if(hasattr(self, 'mine_num_ent%d_%d' % (pkx, pky))):
                ent = getattr(self, 'mine_num_ent%d_%d' % (pkx, pky))
                ent.destroy()
                self.flag_mine[pkx][pky] = 0
            self.minelst[pkx][pky] = 0
            if(self.undo.get()):
                self.undoset()
            if(self.mode == 2):self.minenum_inp(0, 0, 0)
            
    def sel(self, var, label, label2, label3, label4, entx, enty, mine_ety):
        value = var.get()
        if(value==1):
            pkx = 8
            pky = 8
        elif(value==2):
            pkx = 9
            pky = 16
        elif(value==3):
            str_pkx = StringVar()
            str_pky = StringVar()
            try:pkx = int(eval(entx.get()))
            except SyntaxError:pkx = 16
            try:pky = int(eval(enty.get()))
            except SyntaxError:pky = 30
            if(pkx<4):pkx=4
            elif(pkx>20):pkx=20
            if(pky<4):pky=4
            elif(pky>30):pky=30
            entx.delete(0,END)
            enty.delete(0,END)
            str_pkx.set('%d'%pkx)
            str_pky.set('%d'%pky)
            entx.configure(textvariable=str_pkx)
            enty.configure(textvariable=str_pky)
        else:
            pkx = self.blocksize[0]
            pky = self.blocksize[1]
        self.blocksize[2:4] = [pkx, pky]
        selection = "the Block Size is : " + str(pky) + " X " + str(pkx)
        label.config(text = selection)
        selection = "(1~%d)"%(pkx*pky - 1)
        label2.config(text = selection)
        selection = "%d"%(int((pkx*pky)/div - sub))
        label3.config(text = selection)
        var2 = IntVar()
        var2.set(3)
        self.enl(var2, label4, mine_ety)
        
    def enl(self, var, label, mine_ety):
        value = var.get()
        if(value==1):num = int((self.blocksize[2]*self.blocksize[3])/div - sub)
        elif(value==2):
            str_ety = StringVar()
            try:num = int(eval(mine_ety.get()))
            except SyntaxError:num = int((self.blocksize[2]*self.blocksize[3])/div - sub)
            if(num<1):num = 1
            elif(num>=self.blocksize[2]*self.blocksize[3]):num = self.blocksize[2]*self.blocksize[3] - 1
            #mine_ety.delete(0,END)
            str_ety.set('%d'%num)
            mine_ety.configure(textvariable=str_ety)
        elif(self.mineleft>(self.blocksize[2]*self.blocksize[3] - 1)):
            str_ety = StringVar()
            num = self.blocksize[2]*self.blocksize[3] - 1
            #mine_ety.delete(0,END)
            str_ety.set('%d'%num)
            mine_ety.configure(textvariable=str_ety)
        else:num = self.mineleft
        self.mineleft_buf = num
        selection = "the Number of Mines is : " + str(num)
        label.config(text = selection)

    def setflash(self, event, var1, var2, label, label2, label3, label4, entx, enty, mine_ety):
        self.sel(var1, label, label2, label3, label4, entx, enty, mine_ety)
        self.enl(var2, label4, mine_ety)
        
    def setmine(self):
        self.blocksize[2:4]=self.blocksize[0:2]
        clr = 'tan'
        teco = 'black'
        settingwin = Toplevel(self.root, height=300, width=300, bg=clr)
        settingwin.minsize(300,300)
        settingwin.maxsize(300,300)
        settingwin.title('Setting')
        entx = Entry(settingwin, width=3, bd=0, justify=CENTER)
        enty = Entry(settingwin, width=3, bd=0, justify=CENTER)
        mine_ety = Entry(settingwin, width=10, bd=0, justify=CENTER)
        button = Button(settingwin, width=10, height=2, bd = 3, text="OK",
                        command=lambda w=settingwin : self.setok(w))
        button.pack(side = BOTTOM)
        
        var = IntVar()
        var2 = IntVar()

        selection = "(1~%d)"%(self.blocksize[0]*self.blocksize[1] - 1)
        label0 = Label(settingwin, bg=clr, fg=teco, text=selection)
        selection = "the Block Size is : " + str(self.blocksize[1]) + " X " + str(self.blocksize[0])
        label = Label(settingwin, bg=clr, fg=teco, text=selection)
        label.pack(anchor = W)
        selection = "the Number of Mines is : %d"%self.mineleft
        label2 = Label(settingwin, bg=clr, fg=teco, text=selection)
        label25 = Label(settingwin, bg=clr, fg=teco, text='X')
        label3 = Label(settingwin, bg=clr, fg=teco, text=' ')
        label4 = Label(settingwin, bg=clr, fg=teco, text='(4~30)   (4~20)')
        label5 = Label(settingwin, bg=clr, fg=teco, \
                       text='%d'%int((self.blocksize[0]*self.blocksize[1])/div - sub))
        
        
        R1 = Radiobutton(settingwin, text=" 8 X 8", variable=var, value=1, bg=clr, fg=teco,
                         command=lambda v=var, lab=label, lab1=label0, lab2=label5, lab3=label2,
                         ex=entx, ey=enty, em=mine_ety : self.sel(v, lab, lab1, lab2, lab3, ex, ey, em))
        R1.pack(anchor = W)
        R2 = Radiobutton(settingwin, text=" 16 X 9", variable=var, value=2, bg=clr, fg=teco, 
                         command=lambda v=var, lab=label, lab1=label0, lab2=label5, lab3=label2,
                         ex=entx, ey=enty, em=mine_ety : self.sel(v, lab, lab1, lab2, lab3, ex, ey, em))
        R2.pack(anchor = W)
        R3 = Radiobutton(settingwin, text=" self define :", variable=var, value=3, bg=clr, fg=teco, 
                         command=lambda v=var, lab=label, lab1=label0, lab2=label5, lab3=label2,
                         ex=entx, ey=enty, em=mine_ety : self.sel(v, lab, lab1, lab2, lab3, ex, ey, em))
        R3.pack(anchor = W)
        label3.pack(anchor = W)
        label2.pack(anchor = W)
        R4 = Radiobutton(settingwin, text=" use defult mine number :", variable=var2, value=1, bg=clr,
                         fg=teco, command=lambda v=var2, lab=label2, e=mine_ety : self.enl(v, lab, e))
        R4.pack(anchor = W)
        R5 = Radiobutton(settingwin, text=" self define :", variable=var2, value=2, bg=clr, fg=teco, 
                         command=lambda v=var2, lab=label2, e=mine_ety : self.enl(v, lab, e))
        R5.pack(anchor = W)

        button.bind("<Enter>",lambda event, v1=var, v2=var2, lab=label, lab1=label0, lab2=label5,
                    lab3=label2, ex=entx, ey=enty, em=mine_ety : self.setflash(event, v1, v2, lab,
                                                                lab1, lab2, lab3, ex, ey, em))
        label0.place(x=180,y=178)
        label25.place(x=129,y=78)
        label4.place(x=90,y=100)
        label5.place(x=180,y=152)
        entx.place(x=150,y=78)
        enty.place(x=100,y=78)
        mine_ety.place(x=100, y=178)
                          
    def about(self):
        tx0 = "about Mine Sweepping Assist"
        tx1 = "the Author\nhexuanyou\n\nemail: he_xuanyou@163.com\n\nThanks my love\nxiao cong\n\nVersion: 1.0\n\n2017/4/23"
        tkMessageBox.showinfo(tx0.decode("GBK"), tx1.decode("GBK"))

    def gameover(self, pkx ,pky):
        self.mineleft = self.mineleft - 1
        self.var.set('%d'%self.mineleft)
        setattr(self, 'mine_num_dsp%d_%d' % (pkx, pky), Label(self.frame, width=3, 
                  bd=0, justify=CENTER))
        dsp = getattr(self, 'mine_num_dsp%d_%d' % (pkx, pky))
        svar = StringVar()
        svar.set('@')
        dsp.configure(textvariable = svar, fg='red')
        dsp.grid(row=pkx,column=pky)
        self.showmine(1)
        self.ts = 0
        tx0 = "Game Over"
        tx1 = "Game over, restart now ?"
        ans = tkMessageBox.askyesno(tx0.decode("GBK"), tx1.decode("GBK"))
        if(ans):
            self.reset()
            bk = getattr(self, 'b%dk%d'%(pkx, pky))
            bk.destroy()
            self.buinit(pkx, pky)
        else:
            self.flag_assume[pkx][pky] = 1


    def gamewon(self, pkx ,pky):
        te = time.time()
        tx0 = "Congratulation"
        tx1 = "Congratulation! You win\nThe time you take : %ds\n\nRestart or not"%(int(te-self.ts))
        self.ts = 0
        ans = tkMessageBox.askyesno(tx0.decode("GBK"), tx1.decode("GBK"))
        if(ans):
            self.reset()
            bk = getattr(self, 'b%dk%d'%(pkx, pky))
            bk.destroy()
            self.buinit(pkx, pky)

    def helpfile(self):
        helpwin = Toplevel(self.root)
        helpwin.title("Help File")
        test = Text(helpwin, bg="DimGray", fg="white")
        infile = open("./help/help_for_sweep.txt",'r')
        for line in infile.readlines():
            if line[:3] == codecs.BOM_UTF8:
                line = line[3:]
            test.insert(INSERT, line.decode("GBK"))
        infile.close()
        Button(helpwin, text="close", command=helpwin.destroy).pack(side=BOTTOM)
        test.pack()

    def buinit(self, pkx, pky):
        setattr(self, 'b%dk%d' % (pkx, pky), Button(self.frame, width=3, height=1, bg='royalblue'))
        bk = getattr(self, 'b%dk%d' % (pkx, pky))
        bk.grid(row=pkx,column=pky)
        bk.bind("<Enter>",lambda event,x=pkx,y=pky: self.enterKey(event,x,y))
        bk.bind("<Leave>",lambda event,x=pkx,y=pky: self.leaveKey(event,x,y))
        bk.bind("<Button-1>",lambda event,x=pkx,y=pky: self.leftKey(event,x,y))
        bk.bind("<ButtonRelease-1>",lambda event,x=pkx,y=pky: self.leftKeyrelease(event,x,y))
        bk.bind("<Button-3>",lambda event,x=pkx,y=pky: self.rightKey(event,x,y))
        
    def block(self):  #pkx = row, pky = column
        for pkx in range(self.blocksize[0]):
            for pky in range(self.blocksize[1]):
                self.buinit(pkx, pky)
                
############    mode=2  part  start    ############

    def white_space(self, pkx, pky):
        ret = 0
        for i in range(3):
            for j in range(3):
                epx = pkx - 1 + i
                epy = pky - 1 + j
                if(inrange(self.blocksize[0], self.blocksize[1], epx, epy)):
                    if(self.flag_assume[epx][epy]):return 0
        for i in range(3):
            for j in range(3):
                epx = pkx - 1 + i
                epy = pky - 1 + j
                if(inrange(self.blocksize[0], self.blocksize[1], epx, epy)):
                    if(not self.open[epx][epy]):
                        bk = getattr(self, 'b%dk%d'%(epx, epy))
                        bk.configure(bg = 'whitesmoke', relief=SUNKEN, bd=1, state=DISABLED)
                        self.open[epx][epy] = 1
                        self.undo.put(ret)
                        self.undo.put(epy)
                        self.undo.put(epx)
                        setattr(self, 'mine_num_ent%d_%d' % (epx, epy), Entry(self.frame, width=3, 
                                  bd=0, justify=CENTER))
                        ent = getattr(self, 'mine_num_ent%d_%d' % (epx, epy))
                        ent.grid(row=epx,column=epy)
                        ent.bind("<Enter>",lambda event,x=epx,y=epy: self.dsp_enterKey(event,x,y))
                        ent.bind("<KeyRelease>",lambda event,x=epx,y=epy: self.minenum_inp(event,x,y))
                        ent.bind("<Double-1>",lambda event,x=epx,y=epy: self.leftKey_double(event,x,y))
                        ret = 1
        return 1

    def minespace_hint(self, _pki, _pkj):
        if(self.open_assume[_pki][_pkj] and not self.open[_pki][_pkj]):
            bk = getattr(self, 'b%dk%d'%(_pki, _pkj))
            bk.configure(bg = 'lightgreen', text = ' ')
        elif(not self.open[_pki][_pkj] and not self.flag_mine[_pki][_pkj] and not self.flag_assume[_pki][_pkj]):
            bk = getattr(self, 'b%dk%d'%(_pki, _pkj))
            bk.configure(bg = 'royalblue', text = ' ')
        elif(self.flag_mine[_pki][_pkj] and not self.flag_assume[_pki][_pkj] \
             and not self.open_assume[_pki][_pkj]):
            bk = getattr(self, 'b%dk%d'%(_pki, _pkj))
            bk.configure(text = '@', fg = 'black', bg = 'pink')

    def assume_hint(self, open_assume, flag_assume):
        for _pki in range(self.blocksize[0]):
            for _pkj in range(self.blocksize[1]):
                self.flag_mine[_pki][_pkj] = flag_assume[_pki][_pkj]
                self.open_assume[_pki][_pkj] = open_assume[_pki][_pkj]
                self.minespace_hint(_pki, _pkj)
    
    def minenum_inp(self, event, _pki, _pkj):
        if(event != 0):
            if(event.char == ""):return 0
            elif(not self.flag_assume[_pki][_pkj]):
                ent = getattr(self, 'mine_num_ent%d_%d' % (_pki, _pkj))
                try:mine_num = int(eval(event.char))
                except SyntaxError: mine_num = 10
                except NameError: mine_num = 9
                if(mine_num==0):
                    self.minelst[_pki][_pkj] = 0
                    ent.delete(0,END)
                    self.white_space(_pki, _pkj)
                elif(mine_num<0 or mine_num>9):
                    self.minelst[_pki][_pkj] = 0
                    ent.delete(0,END)
                elif(mine_num==9):
                    value = StringVar()
                    value.set('@')
                    ent.configure(textvariable = value, fg='red')
                    self.flag_assume[_pki][_pkj] = 1
                elif(self.magic.checkminenum(self.open, self.flag_assume, mine_num, _pki, _pkj)):
                    self.minelst[_pki][_pkj] = mine_num
                    value = StringVar()
                    value.set('%d'%mine_num)
                    ent.configure(textvariable = value, fg=self.minecolor[mine_num-1])
                else:
                    self.minelst[_pki][_pkj] = 0
                    ent.delete(0,END)
            elif(self.open[_pki][_pkj]):
                ent = getattr(self, 'mine_num_ent%d_%d' % (_pki, _pkj))
                try:mine_num = int(eval(event.char))
                except SyntaxError:mine_num = 9
                except NameError: mine_num = 9
                if(mine_num==0):
                    ent.delete(0,END)
                    self.flag_assume[_pki][_pkj] = 0
                elif(mine_num>0 and mine_num<9):
                    if(self.magic.checkminenum(self.open, self.flag_assume, mine_num, _pki, _pkj)):
                        self.minelst[_pki][_pkj] = mine_num
                        value = StringVar()
                        value.set('%d'%mine_num)
                        ent.configure(textvariable = value, fg=self.minecolor[mine_num-1])
                    else:
                        self.minelst[_pki][_pkj] = 0
                        ent.delete(0,END)
                    self.flag_assume[_pki][_pkj] = 0
                else:
                    value = StringVar()
                    value.set('@')
                    ent.configure(textvariable = value, fg='red')
        self.sweep_algorithm()

    def sweep_algorithm(self):
        if(self.magic.check_primary(self.open, self.flag_assume, self.minelst)):
            self.magic.sweep_primary(self.open, self.flag_assume, self.minelst)
            self.magic.sweep_medium(self.minelst)
            self.magic.sweep_advanced(self.minelst)
            mineleft, flag_mine, open_assume = self.magic.sweep_final(self.minelst)
            self.mineleft = mineleft
            self.var.set('%d'%self.mineleft)
            self.assume_hint(open_assume, flag_mine)
            

############    mode=2  part   ending   ############

    def doubleclick(self, pkx, pky):
        num = minecounter(self.flag_assume, self.blocksize[0], self.blocksize[1], pkx, pky)
        if(num < self.minelst[pkx][pky]):
            for i in range(3):
                for j in range(3):
                    epx = pkx - 1 + i
                    epy = pky - 1 + j
                    if(inrange(self.blocksize[0], self.blocksize[1], epx, epy)):
                        if(not self.open[epx][epy] and not self.flag_assume[epx][epy]):
                            bk = getattr(self, 'b%dk%d'%(epx, epy))
                            bk.configure(bg = 'whitesmoke', relief=SUNKEN, bd=1, state=DISABLED)
        elif(num == self.minelst[pkx][pky]):
            self.exp_search(pkx, pky)
            leftbk = self.blocksize[0]*self.blocksize[1]
            for x in self.open:
                            leftbk = leftbk - sum(x)
            if(leftbk==self.mineleft_buf):self.gamewon(pkx, pky)

    def doubleclick_res(self, pkx, pky):
        for i in range(3):
            for j in range(3):
                epx = pkx - 1 + i
                epy = pky - 1 + j
                if(inrange(self.blocksize[0], self.blocksize[1], epx, epy)):
                    if(not self.open[epx][epy] and not self.flag_assume[epx][epy]):
                        bk = getattr(self, 'b%dk%d'%(epx, epy))
                        bk.configure(relief=RAISED, state=NORMAL, bd=2, bg='royalblue')   
    
    def exp_search(self, pkx, pky):
        ret = 1
        for i in range(3):
            for j in range(3):
                epx = pkx - 1 + i
                epy = pky - 1 + j
                if(inrange(self.blocksize[0], self.blocksize[1], epx, epy)):
                    if(self.open[epx][epy] == 0 and not self.flag_assume[epx][epy] and ret):
                        ret = self.explode(epx, epy)

    def explode(self, pkx, pky):
        ret = 1
        bk = getattr(self, 'b%dk%d' % (pkx, pky))
        bk.configure(bg = 'whitesmoke', relief=SUNKEN, bd=1, state=DISABLED)
        self.open[pkx][pky] = 1
        if(self.flag_mine[pkx][pky] and not self.flag_assume[pkx][pky]):
            ret = 0
            self.gameover(pkx, pky)
        elif(self.minelst[pkx][pky]>0):
            svar = StringVar()
            svar.set('%d'%self.minelst[pkx][pky])
            setattr(self, 'mine_num_dsp%d_%d' % (pkx, pky), Label(self.frame, width=3, 
                    bd=0, justify=CENTER))
            dsp = getattr(self, 'mine_num_dsp%d_%d' % (pkx, pky))
            dsp.grid(row=pkx,column=pky)
            dsp.configure(textvariable = svar, fg=self.minecolor[self.minelst[pkx][pky]-1])
            dsp.bind("<Button-1>",lambda event,x=pkx,y=pky: self.dsp_leftKey(event,x,y))
            dsp.bind("<ButtonRelease-1>",lambda event,x=pkx,y=pky: self.dsp_leftKey_res(event,x,y))
            dsp.bind("<Button-3>",lambda event,x=pkx,y=pky: self.dsp_rightKey(event,x,y))
            dsp.bind("<ButtonRelease-3>",lambda event,x=pkx,y=pky: self.dsp_rightKey_res(event,x,y))
            dsp.bind("<Leave>",lambda event,x=pkx,y=pky: self.dsp_leaveKey(event,x,y))
            dsp.bind("<Enter>",lambda event,x=pkx,y=pky: self.dsp_enterKey(event,x,y))
        else:
            self.exp_search(pkx, pky)
        return ret
                    
    def gamestate(self, pkx, pky):
        ##Game start
        if(self.game_state == 0):
            self.game_state = 1
            self.mineleft_buf = self.mineleft
            self.game = GAME(self.blocksize[0:2], self.mineleft)
            self.flag_mine, self.minelst = self.game.mine_array_gen(pkx, pky)
            self.ts = time.time()
        ##Game in progress
        self.explode(pkx, pky)
        ##Game ending
        leftbk = self.blocksize[0]*self.blocksize[1]
        for x in self.open:
            leftbk = leftbk - sum(x)
        if(leftbk==self.mineleft_buf):self.gamewon(pkx, pky)
             
                
    def rightKey(self, event, pkx, pky):
        if(self.mode == 1):
            if(self.open[pkx][pky] == 0):
                bk = getattr(self, 'b%dk%d'%(pkx, pky))
                if(self.flag_assume[pkx][pky] == 0 and self.mineleft > 0):
                    bk.configure(text='|>', fg='red')
                    self.flag_assume[pkx][pky] = 1
                    self.mineleft = self.mineleft - 1
                    self.right_flag[pkx][pky] = 1
                elif(self.flag_assume[pkx][pky] and self.right_flag[pkx][pky] == 1):
                    bk.configure(text='?', fg = "white", bg = 'royalblue')
                    self.right_flag[pkx][pky] = 2
                elif(self.flag_assume[pkx][pky] and self.right_flag[pkx][pky] == 2):
                    bk.configure(text=' ', bg = 'lightblue')
                    self.flag_assume[pkx][pky] = 0
                    self.mineleft = self.mineleft + 1
                    self.right_flag[pkx][pky] = 0
                self.var.set('%d'%self.mineleft)
        else:
            if(self.open_assume[pkx][pky] == 0):
                bk = getattr(self, 'b%dk%d'%(pkx, pky))
                if(self.flag_assume[pkx][pky] == 0 and self.mineleft > 0):
                    bk.configure(text='|>', fg='red', bg = 'lightblue')
                    self.flag_assume[pkx][pky] = 1
                    self.mineleft = self.mineleft - 1
                elif(self.flag_assume[pkx][pky]):
                    bk.configure(text=' ')
                    self.flag_assume[pkx][pky] = 0
                    self.mineleft = self.mineleft + 1
                self.var.set('%d'%self.mineleft)
                self.minenum_inp(0, 0, 0)
            
    def leftKey(self, event, pkx, pky):
        self.pk[4:6] = [pkx, pky]
        if(not self.open[pkx][pky]):
            bk = getattr(self, 'b%dk%d'%(pkx, pky))
            bk.configure(bg = 'whitesmoke', relief=SUNKEN, bd=1, state=DISABLED)
            
    def leftKey_double(self, event, pkx, pky):
        self.white_space(pkx, pky)
        self.minenum_inp(0, 0, 0)

    def leftKeyrelease(self, event, pkx, pky):
        self.pk[4:8] = [-1, -1, pkx, pky]
        if((self.pk[2:4] != [pkx, pky] or self.pk[0:2] == self.pk[2:4]) and not self.open[pkx][pky]):
            if(self.mode == 1 and self.flag_mine[pkx][pky] and self.flag_assume[pkx][pky] == 0):
                bk = getattr(self, 'b%dk%d'%(pkx, pky))
                bk.configure(bg = 'whitesmoke', relief=SUNKEN, bd=1, state=DISABLED)
                self.open[pkx][pky] = 1
                self.gameover(pkx, pky)
            elif(self.mode == 1 and self.flag_assume[pkx][pky] == 0):
                self.gamestate(pkx, pky)
            elif(self.mode == 2 and self.flag_assume[pkx][pky] == 0):
                bk = getattr(self, 'b%dk%d'%(pkx, pky))
                bk.configure(bg = 'whitesmoke', relief=SUNKEN, bd=1, state=DISABLED)
                self.open[pkx][pky] = 1
                self.undo.put(0)
                self.undo.put(pky)
                self.undo.put(pkx)
                setattr(self, 'mine_num_ent%d_%d' % (pkx, pky), Entry(self.frame, width=3, 
                          bd=0, justify=CENTER))
                ent = getattr(self, 'mine_num_ent%d_%d' % (pkx, pky))
                ent.grid(row=pkx,column=pky)
                ent.bind("<Enter>",lambda event,x=pkx,y=pky: self.dsp_enterKey(event,x,y))
                ent.bind("<KeyRelease>",lambda event,x=pkx,y=pky: self.minenum_inp(event,x,y))
                ent.bind("<Double-1>",lambda event,x=pkx,y=pky: self.leftKey_double(event,x,y))
                self.minenum_inp(0, 0, 0)
            elif(self.flag_assume[pkx][pky]):
                bk = getattr(self, 'b%dk%d' % (pkx, pky))
                bk.configure(bg = 'lightblue', relief=RAISED, bd=2, state=NORMAL)
        elif(not self.open[pkx][pky] and self.flag_assume[pkx][pky]):
            bk = getattr(self, 'b%dk%d' % (pkx, pky))
            bk.configure(bg = 'lightblue', relief=RAISED, bd=2, state=NORMAL)
        elif(not self.open[pkx][pky]):
            bk = getattr(self, 'b%dk%d' % (pkx, pky))
            bk.configure(bg = 'royalblue', relief=RAISED, bd=2, state=NORMAL)

        
    def enterKey(self, event, pkx, pky):
        self.pk[0:2] = [pkx, pky]
        self.var_pk.set('%d, %d'%(pkx+1, pky+1))
        if(not self.open[pkx][pky] and self.pk[2:4] != [pkx, pky]):
            bk = getattr(self, 'b%dk%d' % (pkx, pky))
            bk.configure(bg = 'lightblue')
            
    def leaveKey(self, event, pkx, pky):
        self.pk[0:4] = [-1, -1, pkx, pky]
        self.var_pk.set(' ')
        if(self.mode==1 and not self.open[pkx][pky] and (not self.flag_assume[pkx][pky] \
           or self.right_flag[pkx][pky] != 1) and self.pk[4:6]!=[pkx, pky]):
            bk = getattr(self, 'b%dk%d' % (pkx, pky))
            bk.configure(bg = 'royalblue')
        elif(self.mode==2):
            self.minespace_hint(pkx, pky)

    def dsp_leftKey(self, event, pkx, pky):
        if(self.seed):
            self.doubleclick(pkx, pky)
        self.seed = self.seed + 1

    def dsp_leftKey_res(self, event, pkx, pky):
        self.doubleclick_res(pkx, pky)
        self.seed = self.seed - 1

    def dsp_rightKey(self, event, pkx, pky):
        if(self.seed):
            self.doubleclick(pkx, pky)
        self.seed = self.seed + 1

    def dsp_rightKey_res(self, event, pkx, pky):
        self.doubleclick_res(pkx, pky)
        self.seed = self.seed - 1

    def dsp_leaveKey(self, event, pkx, pky):
        if(self.seed==2):
            self.doubleclick_res(pkx, pky)
        self.seed = 0

    def dsp_enterKey(self, event, pkx, pky):
        self.var_pk.set('%d, %d'%(pkx+1, pky+1))
        self.seed = 0
        

class GAME:
    def __init__(self, bksize, meleft):
        self.blocksize = bksize
        self.mineleft = meleft

    def mine_array_gen(self, x, y):     #x=row, y=column
        lista = [1]*self.mineleft+[0]*(self.blocksize[0]*self.blocksize[1]-self.mineleft-1)
        random.shuffle(lista)
        lista.insert(x*self.blocksize[1]+y, 0)
        mine_flag = array_gen(lista, self.blocksize[0], self.blocksize[1])
        minelst = self.countmine(mine_flag)
        return mine_flag, minelst

    def countmine(self, flag_mine):
        ar_mine_flag = aro_array_gen(flag_mine, self.blocksize[0], self.blocksize[1], 0)
        listc = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
        for i in range(self.blocksize[0]):
            for j in range(self.blocksize[1]):
                listc[i][j] =  searchmine(i, j , ar_mine_flag)
        return listc
        
############################################################################################
###                                     Magic                                            ### 
############################################################################################
class Magic:
    def __init__(self, bksize, meleft):
        self.blocksize = bksize
        self.mineleft = meleft
        self.flag_assume = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
        self.open_assume = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
        self.flag_assume_hist = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
        self.open_assume_hist = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
        self.mine_lst_hist = [[0 for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
        self.final_space = [[False for i in range(self.blocksize[1])] for i in range(self.blocksize[0])]
        self.final_left = meleft

################################################
#############< primary level >##################
################################################

    def check_primary(self, bkopen, flag_mine, mine_lst):
        if(bkopen!=self.open_assume_hist):
            ret_open = 1
            for i in range(self.blocksize[0]):
                self.open_assume_hist[i][0:self.blocksize[1]] = bkopen[i][0:self.blocksize[1]]
        else:ret_open = 0
        if(flag_mine!=self.flag_assume_hist):
            ret_flag = 1
            for i in range(self.blocksize[0]):
                self.flag_assume_hist[i][0:self.blocksize[1]] = flag_mine[i][0:self.blocksize[1]]
        else:ret_flag = 0
        if(mine_lst!=self.mine_lst_hist):
            ret_lst = 1
            for i in range(self.blocksize[0]):
                self.mine_lst_hist[i][0:self.blocksize[1]] = mine_lst[i][0:self.blocksize[1]]
        else:ret_lst = 0
        ret = ret_open or ret_flag or ret_lst
        return ret

    def findout_and_open(self, mine_lst, pkx ,pky):
        black_sp = 0    #count the black space
        mine_num = 0    #the number of mine found
        ret = 0
        for i in range(3):
            for j in range(3):
                epx = pkx - 1 + i
                epy = pky - 1 + j
                if(inrange(self.blocksize[0], self.blocksize[1], epx, epy)):
                    black_sp = black_sp + (not self.open_assume[epx][epy] and not self.flag_assume[epx][epy])
                    mine_num = mine_num + self.flag_assume[epx][epy]
        if(black_sp > 0 and black_sp == mine_lst[pkx][pky] - mine_num):
            self.findout_or_open(pkx, pky, 1)
            ret = 1
        elif(black_sp > 0 and mine_num == mine_lst[pkx][pky]):
            self.findout_or_open(pkx, pky, 2)
            ret = 1
        return ret
        
    def findout_or_open(self, pkx ,pky, level):
        for i in range(3):
            for j in range(3):
                epx = pkx - 1 + i
                epy = pky - 1 + j
                if(inrange(self.blocksize[0], self.blocksize[1], epx, epy)):
                    if(level==1 and not self.open_assume[epx][epy] and not self.flag_assume[epx][epy]):
                        self.flag_assume[epx][epy] = 1
                    elif(level==2 and not self.open_assume[epx][epy] and not self.flag_assume[epx][epy]):
                        self.open_assume[epx][epy] = 1
    
    def sweep_primary(self, bkopen, flag_mine, mine_lst):
        ret = 0
        for i in range(self.blocksize[0]):
            self.flag_assume[i][0:self.blocksize[1]] = flag_mine[i][0:self.blocksize[1]]
            self.open_assume[i][0:self.blocksize[1]] = bkopen[i][0:self.blocksize[1]]
        for i in range(self.blocksize[0]):
            for j in range(self.blocksize[1]):
                if(mine_lst[i][j]>0 and mine_lst[i][j]<9):
                    ret0 = self.findout_and_open(mine_lst, i, j)
                    ret = ret or ret0
        if(ret):
            self.sweep_primary(self.open_assume, self.flag_assume, mine_lst)

###############################################
#############< medium level >##################
###############################################

    def iswhitespace(self, black_lst, mine_num, A1, A2):
        mine_right_max = mine_num[2] + black_lst[2]
        mine_left_max = mine_num[0] + black_lst[0]
        left = (black_lst[0] > 0) and ((A1 - mine_num[0]) == (A2 - mine_right_max))
        right = (black_lst[2] > 0) and ((A1 - mine_left_max) == (A2 - mine_num[2]))
        return left, right
    def ismine(self, black_lst, mine_num, A1, A2):
        mine_mid_max_left = A1 - mine_num[0]
        mine_mid_max_right = A2 - mine_num[2]
        mine_right_max = mine_num[2] + black_lst[2]
        mine_left_max = mine_num[0] + black_lst[0]
        
        left = (black_lst[0] > 0) and (mine_mid_max_left > mine_mid_max_right) and \
                (A1 - mine_mid_max_right == mine_left_max)
        right = (black_lst[2] > 0) and (mine_mid_max_left < mine_mid_max_right) and \
                (A2 - mine_mid_max_left == mine_right_max)
        return left, right

    def gemini_right(self, ar_open_assume, ar_flag_assume, mine_lst, pkx, pky):
        ret = 0
        black_sp = [[0 for i in range(4)] for i in range(3)]
        mine_num = [0, 0, 0]
        black_lst = [0, 0, 0]
        for i in range(3):
            for j in range(4):
                black_sp[i][j] = not ar_flag_assume[pkx+i][pky+j] and not ar_open_assume[pkx+i][pky+j]
        black_lst[1] = black_sp[0][1] + black_sp[0][2] + black_sp[2][1] + black_sp[2][2]
        if(black_lst[1] == 0): return ret
        black_lst[0] = black_sp[0][0] + black_sp[1][0] + black_sp[2][0]
        black_lst[2] = black_sp[0][3] + black_sp[1][3] + black_sp[2][3]
        mine_num[0] = ar_flag_assume[pkx][pky] + ar_flag_assume[pkx+1][pky] + ar_flag_assume[pkx+2][pky]
        mine_num[1] = ar_flag_assume[pkx][pky+1] + ar_flag_assume[pkx][pky+2] + \
                      ar_flag_assume[pkx+2][pky+1] + ar_flag_assume[pkx+2][pky+2]
        mine_num[2] = ar_flag_assume[pkx][pky+3] + ar_flag_assume[pkx+1][pky+3] + ar_flag_assume[pkx+2][pky+3]
        left_w, right_w = self.iswhitespace(black_lst, mine_num, mine_lst[pkx][pky], mine_lst[pkx][pky+1])
        left_m, right_m = self.ismine(black_lst, mine_num, mine_lst[pkx][pky], mine_lst[pkx][pky+1])
        ### Left is white space
        if(left_w):
            ret = 1
            for i in range(3):
                if(black_sp[i][0]):ar_open_assume[pkx+i][pky] = 1
        ### Left is mine space
        elif(left_m):
            ret = 1
            for i in range(3):
                if(black_sp[i][0]):ar_flag_assume[pkx+i][pky] = 1
        ### Right is white space
        if(right_w):
            ret = 1
            for i in range(3):
                if(black_sp[i][3]):ar_open_assume[pkx+i][pky+3] = 1
        ### Right is mine space
        elif(right_m):
            ret = 1
            for i in range(3):
                if(black_sp[i][3]):ar_flag_assume[pkx+i][pky+3] = 1
        return ret

    def gemini_down(self, ar_open_assume, ar_flag_assume, mine_lst, pkx, pky):
        ret = 0
        black_sp = [[0 for i in range(3)] for i in range(4)]
        mine_num = [0, 0, 0]
        black_lst = [0, 0, 0]
        for i in range(4):
            for j in range(3):
                black_sp[i][j] = not ar_flag_assume[pkx+i][pky+j] and not ar_open_assume[pkx+i][pky+j]
        black_lst[1] = black_sp[1][0] + black_sp[1][2] + black_sp[2][0] + black_sp[2][2]
        if(black_lst[1] == 0): return ret
        black_lst[0] = black_sp[0][0] + black_sp[0][1] + black_sp[0][2]
        black_lst[2] = black_sp[3][0] + black_sp[3][1] + black_sp[3][2]
        mine_num[0] = ar_flag_assume[pkx][pky] + ar_flag_assume[pkx][pky+1] + ar_flag_assume[pkx][pky+2]
        mine_num[1] = ar_flag_assume[pkx+1][pky] + ar_flag_assume[pkx+1][pky+2] + \
                      ar_flag_assume[pkx+2][pky] + ar_flag_assume[pkx+2][pky+2]
        mine_num[2] = ar_flag_assume[pkx+3][pky] + ar_flag_assume[pkx+3][pky+1] + ar_flag_assume[pkx+3][pky+2]
        left_w, right_w = self.iswhitespace(black_lst, mine_num, mine_lst[pkx][pky], mine_lst[pkx+1][pky])
        left_m, right_m = self.ismine(black_lst, mine_num, mine_lst[pkx][pky], mine_lst[pkx+1][pky])
        ### Left is white space
        if(left_w):
            ret = 1
            for i in range(3):
                if(black_sp[0][i]):ar_open_assume[pkx][pky+i] = 1
        ### Left is mine space
        elif(left_m):
            ret = 1
            for i in range(3):
                if(black_sp[0][i]):ar_flag_assume[pkx][pky+i] = 1
        ### Right is white space
        if(right_w):
            ret = 1
            for i in range(3):
                if(black_sp[3][i]):ar_open_assume[pkx+3][pky+i] = 1
        ### Right is mine space
        elif(right_m):
            ret = 1
            for i in range(3):
                if(black_sp[3][i]):ar_flag_assume[pkx+3][pky+i] = 1
        return ret

    def gemini_right_double(self, ar_open_assume, ar_flag_assume, mine_lst, pkx, pky):
        ret = 0
        black_sp = [[0 for i in range(5)] for i in range(3)]
        mine_num = [0, 0, 0]
        black_lst = [0, 0, 0]
        for i in range(3):
            for j in range(5):
                black_sp[i][j] = not ar_flag_assume[pkx+i][pky+j] and not ar_open_assume[pkx+i][pky+j]
        black_lst[1] = black_sp[0][2] + black_sp[1][2] + black_sp[2][2]
        if(black_lst[1] == 0): return ret
        black_lst[0] = black_sp[0][0] + black_sp[0][1] + black_sp[1][0] + black_sp[2][0] + black_sp[2][1]
        black_lst[2] = black_sp[0][3] + black_sp[0][4] + black_sp[1][4] + black_sp[2][3] + black_sp[2][4]
        mine_num[0] = ar_flag_assume[pkx][pky] + ar_flag_assume[pkx][pky+1] + ar_flag_assume[pkx+1][pky] + \
                      ar_flag_assume[pkx+2][pky] + ar_flag_assume[pkx+2][pky+1]
        mine_num[1] = ar_flag_assume[pkx][pky+2] + ar_flag_assume[pkx+1][pky+2] + ar_flag_assume[pkx+2][pky+2]
        mine_num[2] = ar_flag_assume[pkx][pky+3] + ar_flag_assume[pkx][pky+4] + ar_flag_assume[pkx+1][pky+4] + \
                      ar_flag_assume[pkx+2][pky+3] + ar_flag_assume[pkx+2][pky+4]
        left_w, right_w = self.iswhitespace(black_lst, mine_num, mine_lst[pkx][pky], mine_lst[pkx][pky+2])
        left_m, right_m = self.ismine(black_lst, mine_num, mine_lst[pkx][pky], mine_lst[pkx][pky+2])
        ### Left is white space
        if(left_w):
            ret = 1
            for i in range(3):
                for j in range(2):
                    if(black_sp[i][j]):ar_open_assume[pkx+i][pky+j] = 1
        ### Left is mine space
        elif(left_m):
            ret = 1
            for i in range(3):
                for j in range(2):
                    if(black_sp[i][j]):ar_flag_assume[pkx+i][pky+j] = 1
        ### Right is white space
        if(right_w):
            ret = 1
            for i in range(3):
                for j in range(2):
                    if(black_sp[i][3+j]):ar_open_assume[pkx+i][pky+3+j] = 1
        ### Right is mine space
        elif(right_m):
            ret = 1
            for i in range(3):
                for j in range(2):
                    if(black_sp[i][3+j]):ar_flag_assume[pkx+i][pky+3+j] = 1
        return ret

    def gemini_down_double(self, ar_open_assume, ar_flag_assume, mine_lst, pkx, pky):
        ret = 0
        black_sp = [[0 for i in range(3)] for i in range(5)]
        mine_num = [0, 0, 0]
        black_lst = [0, 0, 0]
        for i in range(5):
            for j in range(3):
                black_sp[i][j] = not ar_flag_assume[pkx+i][pky+j] and not ar_open_assume[pkx+i][pky+j]
        black_lst[1] = black_sp[2][0] + black_sp[2][1] + black_sp[2][2]
        if(black_lst[1] == 0): return ret
        black_lst[0] = black_sp[0][0] + black_sp[0][1] + black_sp[0][2] + black_sp[1][0] + black_sp[1][2]
        black_lst[2] = black_sp[3][0] + black_sp[3][2] + black_sp[4][0] + black_sp[4][1] + black_sp[4][2]
        mine_num[0] = ar_flag_assume[pkx][pky] + ar_flag_assume[pkx][pky+1] + ar_flag_assume[pkx][pky+2] + \
                      ar_flag_assume[pkx+1][pky] + ar_flag_assume[pkx+1][pky+2]
        mine_num[1] = ar_flag_assume[pkx+2][pky] + ar_flag_assume[pkx+2][pky+1] + ar_flag_assume[pkx+2][pky+2]
        mine_num[2] = ar_flag_assume[pkx+3][pky] + ar_flag_assume[pkx+3][pky+2] + ar_flag_assume[pkx+4][pky] + \
                      ar_flag_assume[pkx+4][pky+1] + ar_flag_assume[pkx+4][pky+2]
        left_w, right_w = self.iswhitespace(black_lst, mine_num, mine_lst[pkx][pky], mine_lst[pkx+2][pky])
        left_m, right_m = self.ismine(black_lst, mine_num, mine_lst[pkx][pky], mine_lst[pkx+2][pky])
        ### Left is white space
        if(left_w):
            ret = 1
            for i in range(2):
                for j in range(3):
                    if(black_sp[i][j]):ar_open_assume[pkx+i][pky+j] = 1
        ### Left is mine space
        elif(left_m):
            ret = 1
            for i in range(2):
                for j in range(3):
                    if(black_sp[i][j]):ar_flag_assume[pkx+i][pky+j] = 1
        ### Right is white space
        if(right_w):
            ret = 1
            for i in range(2):
                for j in range(3):
                    if(black_sp[i+3][j]):ar_open_assume[pkx+3+i][pky+j] = 1
        ### Right is mine space
        elif(right_m):
            ret = 1
            for i in range(2):
                for j in range(3):
                    if(black_sp[i+3][j]):ar_flag_assume[pkx+3+i][pky+j] = 1
        return ret

    def sweep_medium(self, mine_lst):
        ret = 0
        ar_open_assume = aro_array_gen(self.open_assume, self.blocksize[0], self.blocksize[1], 1)
        ar_flag_assume = aro_array_gen(self.flag_assume, self.blocksize[0], self.blocksize[1], 0)
        #{A[i,j],A[i,j+1]}
        for i in range(self.blocksize[0]):
            for j in range(self.blocksize[1]-1):
                if(mine_lst[i][j]>0 and mine_lst[i][j]<9 and mine_lst[i][j+1]>0 and mine_lst[i][j+1]<9):
                    ret0 = self.gemini_right(ar_open_assume, ar_flag_assume, mine_lst, i, j)
                    ret = ret or ret0
        #{A[i,j],A[i+1,j]}
        for i in range(self.blocksize[0]-1):
            for j in range(self.blocksize[1]):
                if(mine_lst[i][j]>0 and mine_lst[i][j]<9 and mine_lst[i+1][j]>0 and mine_lst[i+1][j]<9):
                    ret0 = self.gemini_down(ar_open_assume, ar_flag_assume, mine_lst, i, j)
                    ret = ret or ret0
        #{A[i,j],A[i,j+2]}
        for i in range(self.blocksize[0]):
            for j in range(self.blocksize[1]-2):
                if(mine_lst[i][j]>0 and mine_lst[i][j]<9 and mine_lst[i][j+2]>0 and mine_lst[i][j+2]<9):
                    ret0 = self.gemini_right_double(ar_open_assume, ar_flag_assume, mine_lst, i, j)
                    ret = ret or ret0
        #{A[i,j],A[i+2,j]}
        for i in range(self.blocksize[0]-2):
            for j in range(self.blocksize[1]):
                if(mine_lst[i][j]>0 and mine_lst[i][j]<9 and mine_lst[i+2][j]>0 and mine_lst[i+2][j]<9):
                    ret0 = self.gemini_down_double(ar_open_assume, ar_flag_assume, mine_lst, i, j)
                    ret = ret or ret0
        for i in range(self.blocksize[0]):
            self.flag_assume[i][0:self.blocksize[1]] = ar_flag_assume[i+1][1:(self.blocksize[1]+1)]
            self.open_assume[i][0:self.blocksize[1]] = ar_open_assume[i+1][1:(self.blocksize[1]+1)]
        
        if(ret):
            self.sweep_medium(mine_lst)
        else:
            self.sweep_primary(self.open_assume, self.flag_assume, mine_lst)


################################################
############< advanced level >##################
################################################

    def count_mine(self, pkx, pky, ar_flag_assume):
        num = 0
        for i in range(3):
            for j in range(3):
                num = num + ar_flag_assume[pkx+i][pky+j]
        return num

    def count_space(self, pkx, pky, ar_open_assume, ar_flag_assume):
        space = [[False for i in range(3)] for i in range(3)]
        for i in range(3):
            for j in range(3):
                space[i][j] = not ar_open_assume[pkx+i][pky+j] and not ar_flag_assume[pkx+i][pky+j]
        return space

    def group_flash(self, num, space, pkx, pky):
        ret = 0
        grp = getattr(self, 'group%d_%d'%(pkx, pky))
        grp_space = grp.group_space_get()
        grp_num = grp.group_num_get()
        if(num!=grp_num):
            ret = 1
            grp.group_num_set(num)
        if(space!=grp_space):
            ret = 1
            grp.group_space_set(space)
        return ret

    def advanced_init(self, mine_lst):
        ret = 0
        ar_open_assume = aro_array_gen(self.open_assume, self.blocksize[0], self.blocksize[1], 1)
        ar_flag_assume = aro_array_gen(self.flag_assume, self.blocksize[0], self.blocksize[1], 0)
        for i in range(self.blocksize[0]):
            for j in range(self.blocksize[1]):
                if(mine_lst[i][j]>0 and mine_lst[i][j]<9):
                    group_mine_num = mine_lst[i][j] - self.count_mine(i, j, ar_flag_assume)
                    if(group_mine_num>0 and not hasattr(self, 'group%d_%d'%(i, j))):
                        ret = 1
                        space = self.count_space(i, j, ar_open_assume, ar_flag_assume)
                        setattr(self, 'group%d_%d'%(i, j), Group([i, j], space, group_mine_num))
                    elif(group_mine_num>0):
                        space = self.count_space(i, j, ar_open_assume, ar_flag_assume)
                        ret0 = self.group_flash(group_mine_num, space, i, j)
                        ret = ret or ret0
                elif(hasattr(self, 'group%d_%d'%(i, j))):
                    grp = getattr(self, 'group%d_%d'%(i, j))
                    space = [[False for i in range(3)] for i in range(3)]
                    grp.group_space_set(space)
                    grp.group_num_set(0)
        return ret

    def group_compare(self, grp1, grp2):
        num1 = grp1.group_num_get()
        num2 = grp2.group_num_get()
        if(num2>num1 or num2==0):return 0
        pkx1, pky1 = grp1.group_lst_get()
        space1 = grp1.group_space_get()
        pkx2, pky2 = grp2.group_lst_get()
        space2 = grp2.group_space_get()
        delta_x = pkx2 - pkx1
        delta_y = pky2 - pky1
        space_tmp = [[False for i in range(3)] for i in range(3)]
        for i in range(3):
            for j in range(3):
                if(i+delta_x >=0 and i+delta_x <= 2 and j+delta_y >= 0 and j+delta_y <= 2):
                    if(space2[i][j] and not space1[i+delta_x][j+delta_y]):return 0
                    elif(space2[i][j]):space_tmp[i+delta_x][j+delta_y] = True
                elif(space2[i][j]):return 0
        num1 = num1 - num2
        grp1.group_num_set(num1)
        if(num1 == 0):
            for i in range(3):
                for j in range(3):
                    if(not space_tmp[i][j] and space1[i][j]):self.open_assume[pkx1-1+i][pky1-1+j] = 1
                    elif(space_tmp[i][j]):space1[i][j] = False
            grp1.group_space_set(space1)
        else:
            space_num = 0
            for i in range(3):
                for j in range(3):
                    if(not space_tmp[i][j] and space1[i][j]):space_num = space_num + 1
                    elif(space_tmp[i][j]):space1[i][j] = False
            if(space_num==num1):
                for i in range(3):
                    for j in range(3):
                        if(not space_tmp[i][j] and space1[i][j]):self.flag_assume[pkx1-1+i][pky1-1+j] = 1
            grp1.group_space_set(space1)
        return 1

    def group_depart(self, pkx, pky):
        ret = 0
        grp1 = getattr(self, 'group%d_%d'%(pkx, pky))
        for i in range(5):
            for j in range(5):
                num1 = grp1.group_num_get()
                if(num1==0):return ret
                if(hasattr(self, 'group%d_%d'%(pkx+i-2, pky+j-2)) and (i!=2 or j!=2)):
                    grp2 = getattr(self, 'group%d_%d'%(pkx+i-2, pky+j-2))
                    ret0 = self.group_compare(grp1, grp2)
                    ret = ret or ret0
        return ret
    
    def advanced_depart(self, mine_lst):
        ret = 0
        for i in range(self.blocksize[0]):
            for j in range(self.blocksize[1]):
                if(mine_lst[i][j]>0 and mine_lst[i][j]<9):
                    if(hasattr(self, 'group%d_%d'%(i, j))):
                        ret0 = self.group_depart(i, j)
                        ret = ret or ret0
        return ret

    def sweep_advanced(self, mine_lst):
        ret = 0
        ret = self.advanced_init(mine_lst)
        while(ret):
            ret = self.advanced_depart(mine_lst)
        self.sweep_medium(mine_lst)

        mineleft = 0
        for x in self.flag_assume:
            mineleft = mineleft + sum(x)
        self.final_left = self.mineleft - mineleft
        

################################################
##############< fantastic level >###############
################################################

    def sweep_fantastic(self, mine_lst):
        for i in range(self.blocksize[0]-2):
            for j in range(self.blocksize[1]-2):
                if(hasattr(self, 'group%d_%d'%(i+1, j+1))):
                    grp = getattr(self, 'group%d_%d'%(i+1, j+1))
                    num = grp.group_num_get()
                    if(num == 3):
                        space = grp.group_space_get()
                        for _pki in range(3):
                            for _pkj in range(3):
                                if(hasattr(self, 'group%d_%d'%(i+_pki, j+_pkj))):
                                    grp1 = getattr(self, 'group%d_%d'%(i+_pki, j+_pkj))
                                    num1 = grp1.group_num_get()
                                    if(num1 == 1):
                                        space1 = grp1.group_space_get()
                                        num = num - 1
                                        for ax in range(3):
                                            for ay in range(3):
                                                if(space1[ax][ay] and ax+_pki-1>=0 and ax+_pki-1<3 \
                                                   and ay+_pkj-1>=0 and ay+_pkj-1<3):
                                                    space[ax+_pki-1][ay+_pkj-1] = 0
                        space_num = 0
                        for t in space:
                            space_num = space_num + sum(t)
                        if(space_num == num and num > 0):
                            grp.group_num_set(0)
                            for bx in range(3):
                                for by in range(3):
                                    if(space[bx][by]):self.flag_assume[i+bx][j+by] = 1
                            for _pki in range(3):
                                for _pkj in range(3):
                                    if(hasattr(self, 'group%d_%d'%(i+_pki, j+_pkj))):
                                        grp1 = getattr(self, 'group%d_%d'%(i+_pki, j+_pkj))
                                        num1 = grp1.group_num_get()
                                        if(num1 == 1):
                                            space1 = grp1.group_space_get()
                                            for ax in range(3):
                                                for ay in range(3):
                                                    if(space1[ax][ay] and (ax+_pki-1<0 or ax+_pki-1>2 \
                                                   or ay+_pkj-1<0 or ay+_pkj-1>2)):
                                                        space1[ax][ay] = 0
                                                        self.open_assume[i+_pki-1+ax][j+_pkj-1+ay] = 1
                                            grp1.group_space_set(space1)
        
                
################################################
###############< final level >##################
################################################

    def final_count_space(self):
        num = 0
        for x in self.final_space:
            num = num + sum(x)
        return num

    def final_compare(self, grp):
        space = grp.group_space_get()
        pkx, pky = grp.group_lst_get()
        for i in range(3):
            for j in range(3):
                if(space[i][j]):
                    if(not self.final_space[pkx-1+i][pky-1+j]):return 0
        for i in range(3):
            for j in range(3):
                if(space[i][j]):self.final_space[pkx-1+i][pky-1+j] = False
        return 1

    def final_depart(self):
        ret = 0
        for i in range(self.blocksize[0]):
            for j in range(self.blocksize[1]):
                if(hasattr(self, 'group%d_%d'%(i, j))):
                    grp = getattr(self, 'group%d_%d'%(i, j))
                    num = grp.group_num_get()
                    if(num>0):ret = self.final_compare(grp)
                    else:ret = 0
                    if(ret):self.final_left = self.final_left - num

    def sweep_final(self, mine_lst):
        ret = 0
        self.sweep_fantastic(mine_lst)
        for i in range(self.blocksize[0]):
            for j in range(self.blocksize[1]):
                self.final_space[i][j] = not self.open_assume[i][j] and not self.flag_assume[i][j]
        self.final_depart()
        num = self.final_count_space()
        if(num == 0):
            mineleft = 0
            for x in self.flag_assume:
                mineleft = mineleft + sum(x)
            self.final_left = self.mineleft - mineleft
            return self.final_left, self.flag_assume, self.open_assume
        if(self.final_left == 0):
            for i in range(self.blocksize[0]):
                for j in range(self.blocksize[1]):
                    if(self.final_space[i][j]):
                        self.open_assume[i][j] = 1
        else:
            if(self.final_left == num):
                for i in range(self.blocksize[0]):
                    for j in range(self.blocksize[1]):
                        if(self.final_space[i][j]):
                            self.flag_assume[i][j] = 1
        self.sweep_advanced(mine_lst)
        mineleft = 0
        for x in self.flag_assume:
            mineleft = mineleft + sum(x)
        self.final_left = self.mineleft - mineleft
        return self.final_left, self.flag_assume, self.open_assume
        
################################################
    
    def checkminenum(self, bkopen, flag_mine, mine_num, pkx, pky):
        count_max = 0
        count_min = 0
        for i in range(3):
            for j in range(3):
                epx = pkx - 1 + i
                epy = pky - 1 + j
                if(inrange(self.blocksize[0], self.blocksize[1], epx, epy)):
                    count_min = count_min + flag_mine[epx][epy]
                    count_max = count_max + flag_mine[epx][epy] + \
                                (not flag_mine[epx][epy] and not bkopen[epx][epy])
        if(mine_num < count_min or mine_num > count_max):return 0
        else:return 1

############################################################################################
###                                          end                                         ### 
############################################################################################

class Group:
    def __init__(self, lst, space, num):
        self.pkx = lst[0]
        self.pky = lst[1]
        self.space = space
        self.mine_num = num
    def group_lst_get(self):
        return self.pkx, self.pky
    def group_num_get(self):
        return self.mine_num
    def group_num_set(self, num):
        self.mine_num = num
    def group_space_get(self):
        return self.space
    def group_space_set(self, space):
        self.space = space

mspGUI = GUI()

mspGUI.root.mainloop()
