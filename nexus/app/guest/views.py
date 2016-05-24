from app.guest import guest
from flask import render_template, flash, redirect, session, g, request, url_for, abort

@guest.route('/')
def show():
    import hashlib
    text = hashlib.md5("yoyo").hexdigest()
    return render_template("temp.html", homeclass="active", temptext=text)

@guest.route('/temp2/')
def temp2():
    from app.models.dbmodels.index_entities import Entity
    print 'should work fine'
    #Entity.del_all_entities()
    en = Entity(4,'Kapil','person,politician','Kapil, Thakkar', 'gujrat iit mumbai')
    rows = en.insertEntity()
    print 'will be here if all fine'
    return render_template("temp.html", homeclass="active", temptext = 'You are here')

@guest.route('/temp3/')
def temp3():
    from app.utils.locprocess import getCityState
    (city,state) = getCityState('pondicherry')
    return render_template("temp.html", homeclass="active", temptext = city+' '+state)

@guest.route('/viz/')
def viz():
    cypher = ''
    return render_template("temp.html", homeclass="active", temptext = city+' '+state)        



