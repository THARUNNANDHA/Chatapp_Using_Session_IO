from flask import Flask,redirect,url_for,render_template,request,session
from flask_socketio import SocketIO,join_room,leave_room,send
from string import ascii_uppercase
import random

app= Flask(__name__)
app.config['SECRET_KEY'] ='tharun1234'
socketio=SocketIO(app)

room_list={}
def creatunique_values(a):
    while True:
        code=''
        for _ in range(a):
            code+=random.choice(ascii_uppercase)
        if code not in room_list:
            break
    return code


@app.route('/', methods=['GET','POST'])
def home():
    session.clear()
    if request.method=='POST':
        name=request.form.get('name')
        code=request.form.get('code')
        join=request.form.get('join',False)
        create=request.form.get('create',False)

        if not name:
            return render_template('home.html',error="pleare enter a name",code=code,name=name)
        
        if join!=False and not code:
            return render_template('home.html',error=" join pleare enter a code", code=code,name=name)
        
        room=code
        if create!=False:
            room=creatunique_values(4)
            room_list[room]={'members':0,'messages':[]}
        elif code not in room_list:
            return render_template('home.html',error='room dose not exist' ,code=code,name=name)
        
        session['room']=room
        session['name']=name
        print(room_list.values())
        return redirect(url_for('room'))

    return render_template('home.html')

@app.route('/room')
def room():
    room=session.get('room')

    if room is None or session.get('name') is None or room not in room_list:
        return render_template('home.html')

    return render_template('room.html', code=room, messages=room_list[room]["messages"])





@socketio.on("message")
def message(data):
    room=session.get("room")
    if room not in room_list:
        return
    content ={
        "name":session.get("name"),
        "message":data["data"]
    }
    send(content,to=room)
    room_list[room]["messages"].append(content)
    print(f"{session.get('name')} said:{data['data']}")

@socketio.on("connect")
def connect():
    room=session.get('room')
    name=session.get('name')
    if not room or not name:
        return
    if room not in room_list:
        leave_room(room)
        return
    join_room(room)
    send({"name":name,"message":'has joined the room'},to=room)
    room_list[room]["members"]+=1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect(): 
    room=session.get('room')
    name=session.get('name')
    leave_room(room)
    
    if room in room_list:
        room_list[room]["members"]-=1
        if room_list[room]["members"]<=0:
            del room_list[room]

    send({"name":name,"message":'has left the room'},to=room)
    print(f"{name} left room {room}")

if __name__ == '__main__':
    socketio.run(app,debug=True)