import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:fryo/src/screens/menu_page.dart';
import 'package:page_transition/page_transition.dart';
import '../shared/styles.dart';
import '../shared/colors.dart';
import 'package:http/http.dart';
import '../screens/base_page.dart';
import '../screens/menu_page.dart';
import '../shared/items.dart';

class CartPage extends StatefulWidget {
  CartPage({Key key}) : super(key: key);

  @override
  _CartPageState createState() => _CartPageState();
}

class _CartPageState extends State<CartPage> {
  int value = 0;
  List<ItemData> cartList = [];

  @override
  Widget build(BuildContext context) {
    print(cartMap);
    cartList.clear();
    cartMap.forEach((key, value) {
      cartList.add(value);
    });
    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        centerTitle: true,
        elevation: 0,
        backgroundColor: white,
        title: Text('Cart', style: h3, textAlign: TextAlign.center),
      ),
      body: buildMenu(),
    );
  }

  @override
  void dispose() {
    super.dispose();
  }

  Widget buildMenu() {
    return Padding(
      padding: const EdgeInsets.all(10.0),
      child: Column(
        children: <Widget>[
          buildFoodList(),
          Container(
            child: Row(
              children: [
                Text(
                  'Total',
                  style: h5,
                ),
                SizedBox(
                  width: 300,
                ),
                Text(
                  '30',
                  style: h5,
                ),
              ],
            ),
          ),
          Container(
            height: 50,
            margin: EdgeInsets.only(top: 10, bottom: 10),
            padding: EdgeInsets.all(10),
            width: double.infinity,
            color: Colors.greenAccent,
            child: FlatButton(
              child: Text(
                "Place Order",
                style: h8,
              ),
              onPressed: () {
                setState(() {
                  //callback();
                });
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget buildFoodList() {
    return Expanded(
      child: new ListView.builder(
          itemCount: cartList.length,
          itemBuilder: (BuildContext context, int index) {
            return _buildFoodItem(cartList[index]);
          }),
    );
  }

  Widget _buildFoodItem(ItemData item) {
    return Padding(
      padding: EdgeInsets.only(left: 10.0, right: 12.0, top: 12.0),
      child: InkWell(
        onTap: () {},
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: <Widget>[
            Container(
                child: Row(children: <Widget>[
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(item.mItem.name, style: foodNameText),
                SizedBox(
                  height: 5,
                ),
                Padding(
                  padding: const EdgeInsets.only(left: 5.0),
                  child:
                      Text('₹' + item.mItem.price.toString(), style: priceText),
                ),
              ])
            ])),
            Container(
              height: 34,
              width: 80,
              decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade600),
                  borderRadius: BorderRadius.circular(5)),
              child: getCustomContainer(item.mItem),
            )
          ],
        ),
      ),
    );
  }

  Widget getCustomContainer(Item item) {
    if (cartMap.containsKey(item)) {
      return getOneWidget(item);
    } else {
      return getZeroWidget(item);
    }
  }

  Widget getZeroWidget(Item item) {
    return Row(
      children: <Widget>[
        Padding(
          padding: const EdgeInsets.only(left: 12.0),
          child: Text(
            'Add',
            style: h6,
          ),
        ),
        Container(
          width: 25,
          child: IconButton(
              iconSize: 16,
              icon: Icon(
                Icons.add,
                color: primaryColor,
              ),
              color: darkText,
              onPressed: () {
                setState(() {
                  if (cartMap.containsKey(item)) {
                    cartMap[item].quantity++;
                  } else {
                    cartMap[item] = ItemData(1, WidgetMarker.one, item);
                  }
                });
              }),
        ),
      ],
    );
  }

  Widget getOneWidget(Item item) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: <Widget>[
        Container(
          width: 25,
          child: IconButton(
              iconSize: 16,
              icon: Icon(
                Icons.remove,
                color: primaryColor,
              ),
              color: darkText,
              onPressed: () {
                setState(() {
                  if (cartMap[item].quantity > 1) {
                    cartMap[item].quantity--;
                  } else {
                    cartMap.remove(item);
                  }
                });
              }),
        ),
        Padding(
          padding: const EdgeInsets.only(left: 2.0, right: 2),
          child: Text(
            cartMap[item].quantity.toString(),
            style: h6,
          ),
        ),
        Container(
          width: 25,
          child: IconButton(
              iconSize: 16,
              icon: Icon(
                Icons.add,
                color: primaryColor,
              ),
              color: darkText,
              onPressed: () {
                setState(() {
                  if (cartMap.containsKey(item)) {
                    cartMap[item].quantity++;
                  } else {
                    cartMap[item].quantity = 1;
                  }
                });
              }),
        ),
      ],
    );
  }
}
