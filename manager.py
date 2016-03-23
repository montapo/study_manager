#coding:utf-8

import csv
import datetime
import pandas as pd

#TODO:機能別にファイルを分ける(input/output/miscellaneous)
#TODO:visualize by js etc...(ブラウザ表示)
#TODO:カレンダー or ガントチャートを作る
#TODO:タスクを入力後、経験値的なものを表示
#TODO:模試とのfeedbackを実施
#TODO:タスクに優先度を付与（機械学習などで）
#TODO:すればいいタスクをrecommend
#3/17 TODO:コツコツタスクのI/Oを改良
#(TODAYが最新)
#3/17 TODO:現時点でやったコツコツタスクを本日のタスクにうまく組み込む
#TODO:seika.csvの情報をもっとリッチにする
#TODO:難易度をわざわざ数字にする必要ない。easy/normal/hardにすればいいかも
#TODO:repeat機能をきちんと書けるようにする。(もしくはデータベースで調整？)

###databaseのカラム
ID = 0                  #通し番号 
TITLE = 1               #タスク名
SUBJECT = 2             #科目
DATE_BEGIN = 3          #開始日
DIFFICULTY = 4          #難易度(E/N/H)
TASK_KIND = 5           #タスクの種類(コツコツ/集中/模試/Z会)
DATE_END = 6            #期日
NUM_Q = 7               #問題数/ページ数
TASK_GRAD = 8           #タスク傾斜（後々）
REPEAT = 9              #繰り返し数
TASK_GRAD_PATTERN = 10  #タスク傾斜のパターン(後々)
GOAL_SCORE = 11         #目標点
DATE_RETURN = 12        #返却日(模試の場合)
###以下入力によって変更されるものたち#######################
FLAG = 13               #フラグ(タスクが終了したかどうか)
SPENT_TIME = 14         #かかった時間(min)
FINISHED_Q = 15         #解いた問題(NUM_Qの単位に合わせる)

#2000/1/1->yyyy,mm,dd形式にする
def str_to_date(str):
    dates = str.split('/')
    date = datetime.date(int(dates[0]),int(dates[1]),int(dates[2]))
    return date

def change_day(date,int):
    cdate = datetime.date(date.year,date.month,date.day+int)
    return cdate

def diff_date(date1,date2):
    return (date1-date2).days

def register_tasks():
    csvfile = 'database.csv'
    f = open(csvfile, "r")
    reader = csv.reader(f)
    header = next(reader)
    """
    routine/intensive/test/zkai
    """
    Routines = []
    Intensives = []
    Tests = []
    Zkais = []
    for row in reader:
        if(row[FLAG] != "finish"):
            if(row[TASK_KIND] == ''):
                continue
            elif(int(row[TASK_KIND]) == 0):
                Routines.append(row)
            elif(int(row[TASK_KIND]) == 1):
                Intensives.append(row)
            elif(int(row[TASK_KIND]) == 2):
                Tests.append(row)
            elif(int(row[TASK_KIND]) == 3):
                Zkais.append(row)
    f.close()
    return Routines, Tests, Zkais, Intensives

##register_tasksで登録したtaskに関して、期日内に入っているものを表示
##&&範囲内のやつを再構成
##show_routine/show_intensive/show_test
def show_routine(routines,date):
    print "====================《コツコツタスク》===================="
    routine_tasks = []
    for routine in routines:
        if(diff_date(date,str_to_date(routine[DATE_END]))<=0 and diff_date(date,str_to_date(routine[DATE_BEGIN]))>=0):
            task_per_day = 1+int(routine[REPEAT])*int(routine[NUM_Q])/diff_date(str_to_date(routine[DATE_END]),str_to_date(routine[DATE_BEGIN])) 
            #print task_per_day
            start = task_per_day * diff_date(date,str_to_date(routine[DATE_BEGIN]))
            goal = start + task_per_day
            repeat = 1
#TODO リピート機能
            while(start>int(routine[NUM_Q])):
                start -= int(routine[NUM_Q])
            while(goal>int(routine[NUM_Q])):
                goal -= int(routine[NUM_Q])
                repeat += 1
            print repeat
            if(repeat <= int(routine[REPEAT])+1):
                routine_tasks.append(routine)
                if(routine[FINISHED_Q] == ''):
                    print  "ID"+routine[ID]+":"+routine[SUBJECT]+":"+routine[TITLE].decode('utf-8')+":"+str(start)+u"〜"+str(goal)+","+str(repeat)+u"周目...早く始めよう！"
                else:
                    print  "ID"+routine[ID]+":"+routine[SUBJECT]+":"+routine[TITLE].decode('utf-8')+":"+str(start)+u"〜"+str(goal)+","+str(repeat)+u"周目("+str(routine[FINISHED_Q])+u"まで終わってます!)"
    return routine_tasks


def show_intensive(intensives,date):
    print "=================《集中タスク》==============="
    intensive_tasks = []
    for intensive in intensives:
        target_date = change_day(str_to_date(intensive[DATE_BEGIN]),int(intensive[DATE_END]))
        nokori = diff_date(target_date,date)
        if(nokori > 0):
            intensive_tasks.append(intensive)
            print  "ID"+intensive[ID]+":"+intensive[SUBJECT]+":"+intensive[TITLE]+":あと"+str(nokori)+"日で終わらせて！"
        if(nokori<=0):
            intensive_tasks.append(intensive)
            print "ID"+intensive[ID]+":"+intensive[SUBJECT]+":"+intensive[TITLE]+"締め切りを"+str(-nokori)+"過ぎてます！！急いで！"
    return intensive_tasks

def show_test(tests,date):
    print "=====================《模試とか》===================="
    test_tasks = []
    num = 1
    for test in tests:
        target_date = str_to_date(test[DATE_END])
        nokori = diff_date(target_date,date)
        if(nokori > 0 ):
            if(num % 4 == 0):
                print "ID"+test[ID]+":"+test[SUBJECT]+":"+test[TITLE]+":あと"+str(nokori)+"日です！一休み一休み☆彡"
            else:
                print "ID"+test[ID]+":"+test[SUBJECT]+":"+test[TITLE]+":あと"+str(nokori)+"日です！気を抜くな！！"
        if(nokori == 0):
            test_tasks.append(test)
            print "今日は" +test[TITLE]+"の日です。頑張ってね!!!!"
        num += 1
    return test_tasks
 
def show_zkai(zkais,date):
    print "====================《Z会》=================="
    zkai_tasks = []
    num = 1
    for zkai in zkais:
        target_date = str_to_date(zkai[DATE_END])
        nokori = diff_date(target_date,date)
        #残り日数が10日を切ったら表示
        if(nokori > 0 and nokori <10):
            if(num % 4 == 0):
                zkai_tasks.append(zkai)
                print "ID"+zkai[ID]+":"+zkai[SUBJECT]+":"+zkai[TITLE]+":あと"+str(nokori)+"日です！一休み一休み☆彡"
            else:
                zkai_tasks.append(zkai)
                print"ID"+zkai[ID]+":"+zkai[SUBJECT]+":"+zkai[TITLE]+":あと"+str(nokori)+"日です！気を抜くな！！"
        if(nokori<=0):
            zkai_tasks.append(zkai)
            print "ID"+zkai[ID]+":"+zkai[SUBJECT]+":"+zkai[TITLE]+"...締め切りを"+str(-nokori)+"日過ぎてます！！急いで！"
    num += 1
    return zkai_tasks
        
def show_tasks(input_date):
    tasks = []#登録したtask
    tasks_pickup = []#ピックアップしたtask
    #登録したtaskを入力する
    #tasks[0]:routine/tasks[1]:intensive/task[2]:test
    tasks = register_tasks()
    #結果を表示
    Routines = show_routine(tasks[0],input_date)
    Tests = show_test(tasks[1],input_date)
    Zkais = show_zkai(tasks[2],input_date)
    #Intensives = show_intensive(tasks[3],input_date)
    #tasksに登録する
    for routine in Routines:
        tasks_pickup.append(routine)
    for test in Tests:
        tasks_pickup.append(test)
    for zkai in Zkais:
        tasks_pickup.append(zkai)
    #for intensive in Intensives:
    #    tasks_pickup.append(intensive)
    print u"頑張ってねー(^^ゞ)"
    return tasks_pickup

#成果を変換して入力にする
def seika_to_input(str):
    input = str.split('/')
    if (len(input) == 3):
        input.append('')
    return input

###　出力用変数
S_DATE = 0
S_ID = 1
S_SUBJECT = 2
S_TITLE = 3
S_TIME = 4
S_START = 5
S_GOAL = 6
S_NUMBER = 7
S_GENSTART = 8
S_GENGOAL = 9

#### 成果登録(TODO:関数化する)
def input_tasks(date,tasks):
    print(str(date)+"のタスクを記入しますか？y/n")
    flg2 = raw_input()  
    if(flg2 == "y"):
        list_seika = []
        for task in tasks:
            if int(task[TASK_KIND]) == 0:
                print task[ID]+":"+task[SUBJECT]+" "+task[TITLE]+"の、成果を書きな"
                print "(y or n)/時間(min)/開始ページ(問題番号)/終了ページ(問題番号)"
            else:                
                print task[ID]+":"+task[SUBJECT]+" "+task[TITLE]+"の、成果を書きな"
                print "(y or n)/時間(min)/問題数"
            seika = raw_input()#自分の成果をinpu
            ###":q"と書けば終了
            if seika == ":q":break
            input_data = seika_to_input(seika) 
            ### inputがちゃんと行われなかったら再度
            ### ただし、何も入力しなかったら素通り                
            while len(input_data)!=4 and input_data[0]!='':
                 if int(task[TASK_KIND]) == 0:
                    print task[ID]+":"+task[SUBJECT]+" "+task[TITLE]+"の、成果を書きな"
                    print "再度：(y or n)/時間(min)/開始ページ(問題番号)/終了ページ(問題番号)"
                 else:                
                    print task[ID]+":"+task[SUBJECT]+" "+task[TITLE]+"の、成果を書きな"
                    print "再度：(y or n)/時間(min)/問題数"
                    seika = raw_input()
                    input_data = seika_to_input(seika)
            if (input_data[0] == "y"):
                if int(task[TASK_KIND]) == 0:
                    list_seika.append([date,task[ID],task[SUBJECT],task[TITLE],input_data[1],input_data[2],input_data[3],int(input_data[3])-int(input_data[2])+1])
                else:
                    list_seika.append([date,task[ID],task[SUBJECT],task[TITLE],input_data[1],"" ,"" ,input_data[2]])
           #TODO:その他やったタスクを追記する。
        f = open('seika.csv','a')
        writer = csv.writer(f)
        writer.writerows(list_seika)
        f.close()

        #TODO:データテーブルにフラグ付与
        #yesならそのタスクを消去
        #ただしコツコツの場合は要考慮
        list_update = []
        csvfile = 'database.csv'
        f = open(csvfile, "r")
        reader = csv.reader(f)
        for row in reader:
            list_update.append(row)
        f.close()

        for list in list_seika:
            if int(list_update[int(list[1])][TASK_KIND]) == 0:
                list_update[int(list[1])][SPENT_TIME] = list[4]
                # 入力する日付が今日じゃなかったら、更新しない。
                if date == datetime.date.today():
                    list_update[int(list[1])][FINISHED_Q] = list[6]
            else:
                list_update[int(list[1])][FLAG] = "finish"
                list_update[int(list[1])][SPENT_TIME] = list[4]
        fw = open('database.csv',"w")
        writer = csv.writer(fw)
        writer.writerows(list_update)
        fw.close()
     
if __name__ == "__main__":
    #### 今日のタスクを書く
    date_today = datetime.date.today()
    print("今日のタスクは・・・ででん！")
    tasks_today = show_tasks(date_today)
    print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
    input_tasks(date_today,tasks_today)
    #### 他の日のタスクを見たいなら書く
    print("他の日のタスクもみたいですか？？y/n")
    flg = raw_input()
    while(flg == "y"):
        print ("タスクを見たい日付を入力してください!")
        var = raw_input()#日付の入力
        input_date = str_to_date(var)
        tasks = show_tasks(input_date)
        input_tasks(input_date,tasks)
        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
        print("まだ見る？？y/n")
        flg = raw_input()
    print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
    
