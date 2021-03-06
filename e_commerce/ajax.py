# -*- coding: utf-8 -*-

from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from django.conf import settings
import logging, os, re
from django.contrib.sites.models import Site
import datetime
from datetime import date
from e_commerce.models import *
import locale

locale.setlocale(locale.LC_ALL, ('it_IT', 'UTF-8'))

SELECT = '<select id="%s"><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option></select>'
var = "'%s'"
LISTRESULTS = '<tr><td><a href="#show" onclick="allarga(%s)"><img src="%s" width="200px" /></a></td><td id="descrprod"><p id="cart-contents">%s</p><small id="cart-contents">%s</small><br/><p class="category-but"><span onclick="javascript:addcart(%s)">Aggiungi a carrello</span><br/>' % (var,'%s','%s','%s','%s')

@dajaxice_register
def primopiano(request):
    dajax = Dajax()
    primo_piano = Product.objects.filter(primo_piano=True)
    out = '<table width="550px">'
    for i in primo_piano:
        out += '<th><td><h3 id="title-comm">%s</h3></td></th>' % (i.name)
        var = "'%s', document.getElementById('%s').value" % (i.name, i.name)
        try:
            sconto = Discount.objects.get(product=i).discount
            prezzo = i.price - (i.price * sconto/100)
            valore_prezzo = "<em><s>EUR %s</s> EUR %s</em>" % (str(i.price), prezzo)
        except:
            valore_prezzo = "<em>EUR %s</em>" % (str(i.price))
        out += str(LISTRESULTS) % (i.image.url, i.image.url, i.description, valore_prezzo, var)
        out += str(SELECT) % (i.name)
        out += '</td></tr>'
    out += '</table>'
    dajax.assign('#elenco','innerHTML',out)
    out = '<h2 id="title-comm">Primo Piano</h2>'
    dajax.assign('#titolo','innerHTML',out)
    return dajax.json()


@dajaxice_register
def productcategories(request):
    dajax = Dajax()
    tags = Tag.objects.all()
    out = "<p id='cart-contents'><b>Categorie</b></p>"
    f = 0
    for i in tags:
        var = "'%s'" % (i.name)
        num = len(Product.objects.filter(tags=i))
        if num > 7: num = 7
        out += '<p class="category tag%s"><span onclick="javascript:categoryfilter(%s);">%s</span></p>' % (str(num), var, i.name)
    dajax.assign('#productcategories','innerHTML',out)
    return dajax.json()

@dajaxice_register
def filtercat(request, option):
    dajax = Dajax()
    try:
        filtercat = Tag.objects.get(name=option).product_set.all()
        if len(filtercat) == 0:
            out = '<p class="nores">Nessun risultato trovato</p>'
        else:
            out = '<table width="550px">'
            for i in filtercat:
		var = "'%s', document.getElementById('%s').value" % (i.name, i.name)
                out += '<th><td><h3 id="title-comm">%s</h3></td></th>' % (i.name)
                try:
                    sconto = Discount.objects.get(product=i).discount
                    prezzo = i.price - (i.price * sconto/100)
                    valore_prezzo = "<em><s>EUR %s</s> EUR %s</em>" % (str(i.price), prezzo)
                except:
                    valore_prezzo = "<em>EUR %s</em>" % (str(i.price))
                out += str(LISTRESULTS) % (i.image.url, i.image.url, i.description, valore_prezzo, var)
		out += str(SELECT) % (i.name)
		out += '</td></tr>'
            out += '</table>'
    except Exception, e:
        logging.error(e)
        out = '<p class="nores">Nessun risultato trovato</p>'
    dajax.assign('#elenco','innerHTML',out)
    out = "<h2 id='title-comm'>Risultati per <em>%s</em></h2>" % (option)
    dajax.assign('#titolo','innerHTML',out)
    return dajax.json()

@dajaxice_register
def onsale(request):
    dajax = Dajax()
    try:
        filtersale = Discount.objects.all()
        if len(filtersale) == 0:
            out = '<p class="nores">Nessun risultato trovato</p>'
        else:
            out = '<table width="550px">'
            for i in filtersale:
                var = "'%s', document.getElementById('%s').value" % (i.product.name, i.product.name)
                out += '<th><td><h3 id="title-comm">%s</h3></td></th>' % (i.product.name)
                try:
                    sconto = Discount.objects.get(product=i.product).discount
                    prezzo = i.product.price - (i.product.price * sconto/100)
                    valore_prezzo = "<em><s>EUR %s</s>  EUR %s</em>" % (str(i.product.price), prezzo)
                except:
                    valore_prezzo = "<em>EUR %s</em>" % (str(i.product.price))
                out += str(LISTRESULTS) % (i.product.image.url, i.product.image.url, i.product.description, valore_prezzo, var)
                out += str(SELECT) % (i.product.name)
                out += '</td></tr>'
            out += '</table>'
    except Exception, e:
        logging.error(e)
        out = '<p class="nores">Nessun risultato trovato</p>'
    dajax.assign('#elenco','innerHTML',out)
    out = "<h2 id='title-comm'>Risultati per <em>Prodotti Scontati</em></h2>"
    dajax.assign('#titolo','innerHTML',out)
    return dajax.json()

@dajaxice_register
def showcart(request):
    dajax = Dajax()
    try:
        session = Session.objects.get(session_key = request.session.session_key)
        session_cart = Cart.objects.filter(session=session)
    except:
        return dajax.json()
    if len(session_cart) > 0:
        out = '<p id="cart-contents"><b>Carrello Acquisti <img style="vertical-align:middle;" width="20px" src="/media/img/carrello.jpeg"/></b></p>'
        for i in session_cart[0].product.all():
            try:
                sconto = Discount.objects.get(product=i.product).discount
                cost = i.product.price - (i.product.price * sconto/100)
                cost *= float(i.num)
            except Exception, e:
                logging.error(e)
                cost = i.product.price * float(i.num)
            out += '<p id="cart-contents">%s x%s Costo: %s &euro;</p>' % (i.product.name, i.num, cost)
    else:
        out = "<p id='cart-contents'><b>Carrello Vuoto</b></p>"
    dajax.assign('#cart','innerHTML',out)
    return dajax.json()

@dajaxice_register
def emptycart(request, val):
    dajax = Dajax()
    try:
        session = Session.objects.get(session_key = request.session.session_key)
        session_cart = Cart.objects.filter(session=session)
    except:
        return dajax.json()
    if len(session_cart) > 0:
        session_cart[0].delete()
    CartObj.objects.filter(session=session).delete()
    out = "<p id='cart-contents'><b>Carrello Vuoto</b></p>"
    dajax.assign('#cart','innerHTML',out)
    if val == "True":
        dajax.script('acquista()')
    return dajax.json()

@dajaxice_register
def addcart(request, obj, num):
    dajax = Dajax()
    try:
        session = Session.objects.get(session_key = request.session.session_key)
        session_cart = Cart.objects.filter(session=session)
    except:
        return dajax.json()
    if len(session_cart) == 0:
        cartobj = CartObj()
	cartobj.session = session
	cartobj.product = Product.objects.get(name=obj)
        cartobj.num = num
	cartobj.save()
        cart = Cart()
        cart.session = session
	cart.save()
	cart.product = [cartobj]
    else:
        old_products = session_cart[0].product.all()
        if obj in [p.product.name for p in old_products] and old_products.get(product__name=obj).session.session_key == session.session_key:
	    cartobj = old_products.get(product__name=obj)
	    cartobj.num += int(num)
	    cartobj.save()
	else:
	    cartobj = CartObj()
	    cartobj.session = session
	    cartobj.product = Product.objects.get(name=obj)
	    cartobj.num = num
	    cartobj.save()
	    new_prods = [cartobj]
	    for i in old_products:
	        new_prods.append(i)
	    session_cart[0].product = new_prods
    return showcart(request)

@dajaxice_register
def clearoldcart(request):
    dajax = Dajax()
    logging.error("IN CLEAR OLD CART datenow %s" % datetime.now())
    for i in CartObj.objects.all():
        try:
            payed = Cart.objects.get(product=i, session=i.session).payed
        except Exception, e:
            logging.error(e)
            payed = False
        if i.session.expire_date < datetime.now():
            if not payed:
                logging.error("Deleting CartObj %s for expiration time and payed %s" % (i,payed))
                i.delete()
            else:
                logging.error("Not deleting CartObj %s because payed", i)
    for i in Cart.objects.all():
        if i.session.expire_date < datetime.now():
            if not i.payed:
                logging.error("Deleting Cart %s for expiration time and payed %s" % (i,i.payed))
                i.delete()
            else:
                logging.error("Not deleting Cart %s because payed", i)
    return dajax.json()


@dajaxice_register
def acquista(request):
    dajax = Dajax()
    try:
        session = Session.objects.get(session_key = request.session.session_key)
        session_cart = Cart.objects.filter(session=session)
        session_cartobjs = CartObj.objects.filter(session=session)
    except:
        return dajax.json()
    out = ""
    if len(session_cart) > 0 and len(session_cartobjs) > 0:
        cartobj = CartObj.objects.filter(session=session)
        totcost = 0
        for i in cartobj:
            try:
                sconto = Discount.objects.get(product=i.product).discount
                cost = i.product.price - (i.product.price * sconto/100)
                cost *= float(i.num)            
	    except:
  		cost = i.product.price * i.num
	    totcost += cost
            rimuovi = '"%s"' % str(i.id)
            out += "<table><tr><td width='100px'><p><img width='100px' src='%s'></p></td><td width='300px'><p align='center' id='cart-contents'>%s x%s &euro; %s</p></td><td width='100px'><p align='center'><img class='category-but' style='width:15px;' src='/media/img/X.png' onclick='javascript:rimuovi(%s)'></p></td></tr></table>" % (i.product.image.url,i.product,i.num,cost,rimuovi)
        out += "<p align='center' id='cart-contents'>Totale %s &euro;</p>" % totcost
        out += "<br/>"
        out += "<div id='errori-form'></div>"
        out += "<table>"
	out += "<tr><td class='title-payment'><label>   Nome Completo</label></td><td><input type='text' id='full_name'/></td></tr>"
	out += "<tr><td class='title-payment'><label>   Citt&agrave;</label></td><td><input type='text' id='city'/></td></tr>"
	out += "<tr><td class='title-payment'><label>   Indirizzo</label></td><td><input type='text' id='address'/></td></tr>"
	out += "<tr><td class='title-payment'><label>   CAP</label></td><td><input type='text' id='cap'/></td></tr>"
	out += "<tr><td class='title-payment'><label>   Email</label></td><td><input type='text' id='email'/></td></tr>"
	out += "<tr><td class='title-payment'><label>   Recapito Telefonico</label></td><td><input type='text' id='phone'/></td></tr>"
        out += "</table>"
        out += "<br/>"
        out += "<p align='center' class='category-but'><span class='category-but' onclick='proseguipagamento()'>Procedi con il Pagamento</span></p>"
        out += "<br/>"
    else:
        out += "<p align='center' id='cart-contents'>Nessun Prodotto Selezionato</p>"
        out += "<p align='center' class='category-but'><a href='/' class='category-but'>Torna al primo piano</a></p>"
    dajax.assign('#elenco','innerHTML',out)
    titolo = "<h2 id='title-comm'>Acquista Prodotti</h2>"
    dajax.assign('#titolo','innerHTML',titolo)
    dajax.script('showcart()')
    return dajax.json()

@dajaxice_register
def rimuovi(request, objid):
    dajax = Dajax()
    try:
        session = Session.objects.get(session_key = request.session.session_key)
    except:
        return dajax.json()
    cart = CartObj.objects.get(id=int(objid),session=session)
    cart.delete()
    return acquista(request)


from django.core.validators import email_re

def is_valid_email(email):
    if email_re.match(email):
        return True
    return False

@dajaxice_register
def paga(request, full_name, city, address, cap, email, phone):
    dajax = Dajax()
    if not full_name or not city or not address or not cap or not email or not phone or not is_valid_email(email):
        out = "<p class='errorlist'>Compilare correttamente tutti i campi sottostanti</p>"
        dajax.assign('#errori-form','innerHTML',out)
        return dajax.json()
    out = "<p class='correctlist'>Campi compilati correttamente</p>"
    dajax.assign('#errori-form','innerHTML',out)
    try:
        session = Session.objects.get(session_key = request.session.session_key)
        session_cart = Cart.objects.filter(session=session)
    except:
        return dajax.json()
    if len(session_cart) > 0:
        purchasecart = PurchaseCart.objects.filter(cart=session_cart[0])
        if len(purchasecart) > 0:
            purchasecart[0].delete()
        purchase = PurchaseCart()
        purchase.cart = session_cart[0]
        purchase.full_name = full_name
        purchase.city = city
        purchase.address = address
        purchase.cap = cap
        purchase.email = email
        purchase.phone = phone
        purchase.save()
        cartobj = CartObj.objects.filter(session=session)
        totcost = 0
        for i in cartobj:
            try:
                sconto = Discount.objects.get(product=i.product).discount
                cost = i.product.price - (i.product.price * sconto/100)
                cost *= float(i.num)
            except:
                cost = i.product.price * i.num
            totcost += cost
        out = "<p align='center' id='cart-contents'>Clicca sul link sottostante</p>"
        out += "<br/>"
        out += '<table id="paypal-button"><tr><td align="center">'
        out += '<form action="%s" method="post">' % 'paypal_url'
        out += '<input type="hidden" name="amount" value="%s">' % totcost
        out += '<input type="hidden" name="cmd" value="_xclick">'
        out += '<input type="hidden" name="business" value="%s">' % 'paypal_email'
        out += '<input type="hidden" name="item_name" value="">' % full_name
        out += '<input type="hidden" name="currency_code" value="EUR">'
        out += '<input type="hidden" name="return" value="%s">' % "TODO"
        out += '<input type="hidden" name="cancel_return" value="%s">' % "TODO"
        out += '<input type="image" src="/media/img/paypal.png" name="submit" alt="Make payments with PayPal - fast, free and secure!">'
        out += '</form>'
        out += '</td></tr></table>'
        dajax.assign('#elenco','innerHTML',out)
    return dajax.json()

