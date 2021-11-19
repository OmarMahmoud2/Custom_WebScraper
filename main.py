import requests
import re
from tkinter import *
from tkinter import messagebox

root = Tk()
root.title('Haraj Scraper')
root.config(padx=50, pady=50)


canvas = Canvas(root, height=100, width=200)
canvas.grid(column=1, row=0)

title_image = PhotoImage(file="haraj.png")
image = canvas.create_image(100, 30, image=title_image)

var = StringVar(root, value=10)
pages_entry = Entry(root, textvariable=var, relief=RAISED)
pages_entry.grid(column=1, row=1, pady=15)

options1=['Animals', 'Real State', 'Cars', 'Devices', 'All', 'Personal belongings', 'Jobs', 'Services', 'Furniture']
var1= StringVar(root)
var1.set(options1[1])
menu= OptionMenu(root, var1, *options1)
menu.config(height=2, width=15)
menu.grid(column=1, row=2, pady=15)

options=['جده', 'المدينة' , 'عرعر' , 'الجوف' , 'نجران' , 'جيزان' , 'الباحة' , 'عسير', 'أبها', 'حائل' , 'حفر الباطن' , 'ينبع' , 'القصيم' , 'الشرقيه' ,'تبوك' , 'الطايف' , 'الرياض', 'مكه']
var2 = StringVar(root, value='جده')
menu2 = OptionMenu(root, var2, *options)
menu2.config(height=2, width=15)
menu2.grid(column=1, row=3, pady=15)



headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
}

advs = {}
def main(url, page_num, category, city):
    with requests.Session() as req:
        req.headers.update(headers)

        for page in range(1, page_num +1): # increase the number of pages from here.
            params = {
                'queryName': 'detailsPosts_tag_page{}'.format(page),
                'token': '',
                'clientid': '812f41b2-9936-4405-aa9c-378db19b8cc4',
                'version': '8.2.9 , 10 18 - 7 - 21'
            }
            deps = {'Animals':'مواشي وحيوانات وطيور', 'Jobs': 'وظائف', 'Services':'خدمات' , 'Personal belongings': 'مستلزمات شخصية', 'All':' كل الحراج', 'Furniture': 'اثاث',
                        'Cars':'حراج السيارات',
                        'Devices' :'حراج الأجهزة', 'Real State':'حراج العقار'}
            data = {
                "query": "query($tag:String,$page:Int) { posts( tag:$tag, page:$page) {\n\t\titems {\n\t\t\tid status authorUsername title city postDate updateDate hasImage thumbURL authorId bodyHTML bodyTEXT city tags imagesList commentStatus commentCount upRank downRank geoHash geoCity geoNeighborhood\n\t\t}\n\t\tpageInfo {\n\t\t\thasNextPage\n\t\t}\n\t\t} }",
                "variables": {
                    "page": page,
                    "tag": deps[category]
                }
            }
            r = req.post(url, params=params, json=data)
            if r.status_code == 200:
                for i in r.json()['data']['posts']['items']:
                    if i['city'] == str(city):
                        phone = re.search(r"(\d){8,}", i['bodyTEXT'])
                        if phone != None:
                            print(i['city'] + '   ' + i['title'] + '  ' + phone.group(0))
                            advs[i['id']] = [f'{city}', f'{phone.group(0)}']
                        else:
                            print(i['city'] + '   ' + i['title'])
                            advs[i['id']] = [f'{city}', ' ']
                    else:
                        continue
            else:
                exit(f"Page# {page} is not exist, However program stopped.")



def contact(url, advs):
    for id in advs:
        if advs[id][1] == ' ':
            params = {
                'queryName': 'postLikeInfo,postContact',
                'token': '',
                'clientid': '812f41b2-9936-4405-aa9c-378db19b8cc4',
                'version': '8.2.9 , 10 18 - 7 - 21'
            }
            data = {
                "query": "query postLikeInfo_postContact($id: Int!, $token: String,$postId: Int!) {\n\t\t\n\t\tpostLikeInfo(id: $id, token: $token)\n\t\t{ \n                    isLike\n                    total\n                    isFollowing\n                     }\n\t\n\r\n\t\tpostContact(postId: $postId)\n\t\t{ \n                    contactText\n                    contactMobile\n                     }\n\t\n\t}",
                "variables": {
                    "id": id,
                    "postId": id,
                    "token": ""
                }
            }
            r = requests.post(url, params=params, json=data)
            advs[id][1] = r.json()['data']['postContact']['contactMobile']
            print(r.json()['data']['postContact']['contactMobile'] + 'coms from api')
        else:
            print(advs[id][1] + 'comes from dict')

def show_results(advs):
    cate = var1.get()
    top = Toplevel(root)
    top.title(f'Results for {cate}')
    top.minsize(width=400, height=600)
    scrollbar = Scrollbar(top)
    scrollbar.pack(side=RIGHT, fill=Y)
    mylist = Listbox(top, yscrollcommand=scrollbar.set, width=60)
    mylist.pack(side=LEFT, fill=BOTH)
    scrollbar.config(command=mylist.yview)
    for ad in advs:
        mylist.insert(END, f"The phone number is : {advs[ad][1]} The city is : {advs[ad][0]}")
        try:
            with open(f'{cate}_search.txt', 'a') as file:
                file.writelines('\n' + f"The phone number is : {advs[ad][1]} The city is : {advs[ad][0]}")
        except FileNotFoundError or FileExistsError:
            with open(f'{cate}_search.txt', 'w') as file:
                file.writelines('\n' + f"The phone number is : {advs[ad][1]} The city is : {advs[ad][0]}")

def grap(adv):
    pages = int(var.get())
    # if not pages.numeric():
    #     messagebox.showerror(title='Pages error', message='Please Enter a valid number')
    city = var2.get()
    department = var1.get()
    main('https://graphql.haraj.com.sa/', pages, department, city)
    contact('https://graphql.haraj.com.sa/', adv)
    show_results(adv)
    global advs
    advs= {}


btn = Button(root, text='Scrape', command= lambda: grap(advs), height=3, width=25)
btn.grid(column=1, row=5, pady=20)

btn_new = Button(root, text='Exit', height=2, command=root.destroy, width=15)
btn_new.grid(column=1, row=8, pady=20)



root.mainloop()
