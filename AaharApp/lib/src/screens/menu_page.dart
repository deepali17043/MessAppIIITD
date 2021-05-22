import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:page_transition/page_transition.dart';
import '../screens/vendor_page.dart';
import '../shared/styles.dart';
import '../shared/colors.dart';
import 'package:http/http.dart';
import '../shared/items.dart';
import '../screens/base_page.dart';
import '../shared/vendor.dart';

enum WidgetMarker { zero, one }
Map<Item, ItemData> cartMap = new Map();
Map<String, List<Item>> menuMap = new Map();
List<String> categoryList = [];
int total = 0;

class Category {
  List<Item> itemList = [];
  String catName;
  Category({this.catName, this.itemList});
}

class MenuPage extends StatefulWidget {
  // final Destination destination;
  final Vendor vendorName;

  const MenuPage({Key key, this.vendorName}) : super(key: key);

  @override
  _MenuPageState createState() => _MenuPageState(vendorName);
}

class _MenuPageState extends State<MenuPage> {
  Vendor vendorName;
  _MenuPageState(this.vendorName);

  int value = 0;
  int _currentIndex = 0;
  static final Item f1 =
      Item(name: 'Sandwich', price: 25, category: 'Snacks', active: true);
  static final Item f2 =
      Item(name: 'Pasta', price: 20, category: 'Snacks', active: true);
  static final Item f3 =
      Item(name: 'Veg Roll', price: 30, category: 'Mains', active: true);
  List<Item> itemList = [f1, f2, f3];

  @override
  Widget build(BuildContext context) {
    menuMap.clear();
    categoryList.clear();
    categoryList = ['All Items'];
    menuMap['All Items'] = [];
    for (Item i in itemList) {
      if (menuMap.containsKey(i.category)) {
        menuMap[i.category].add(i);
      } else {
        categoryList.add(i.category);
        menuMap[i.category] = [i];
      }
      menuMap['All Items'].add(i);
    }
    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        leading: IconButton(
          icon: Icon(
            Icons.arrow_back,
            color: Colors.black,
          ),
          onPressed: () => Navigator.pop(context, false),
        ),
        centerTitle: true,
        elevation: 0,
        backgroundColor: white,
        title: GestureDetector(
          onTap: () {
            Navigator.pushReplacement(
                context,
                PageTransition(
                    type: PageTransitionType.rightToLeft,
                    child: VendorPage(
                      back: true,
                    )));
          },
          child: Text(vendorName.name, style: h3, textAlign: TextAlign.center),
        ),
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
          buildFoodFilter(),
          buildFoodList(),
        ],
      ),
    );
  }

  Widget buildFoodFilter() {
    return Container(
      height: 50,
      //color: Colors.red,
      child: ListView(
        scrollDirection: Axis.horizontal,
        children: List.generate(categoryList.length, (index) {
          return Padding(
            padding: const EdgeInsets.all(8.0),
            child: ChoiceChip(
              selectedColor: primaryColor,
              labelStyle: TextStyle(
                  color: value == index ? Colors.white : Colors.black),
              label: Text(categoryList[index]),
              selected: value == index,
              onSelected: (selected) {
                setState(() {
                  value = index;
                });
              },
            ),
          );
        }),
      ),
    );
  }

  Widget buildFoodList() {
    return Expanded(
      child: new ListView.builder(
          itemCount: menuMap[categoryList[value]].length,
          itemBuilder: (BuildContext context, int index) {
            return _buildFoodItem(menuMap[categoryList[value]][index]);
          }),
    );
  }

  Widget _buildFoodItem(Item item) {
    return Padding(
      padding: EdgeInsets.only(left: 10.0, right: 12.0, top: 12.0),
      child: Container(
        width: 800,
        child: InkWell(
          onTap: () {},
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: <Widget>[
              Container(
                  child: Row(children: <Widget>[
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(item.name, style: foodNameText),
                  SizedBox(
                    height: 5,
                  ),
                  Padding(
                    padding: const EdgeInsets.only(left: 5.0),
                    child: Text('₹' + item.price.toString(), style: priceText),
                  ),
                ])
              ])),
              Container(
                height: 34,
                width: 90,
                decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey.shade600),
                    borderRadius: BorderRadius.circular(5)),
                child: getCustomContainer(item),
              )
            ],
          ),
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
    return GestureDetector(
      onTap: () {
        {
          setState(() {
            if (cartMap.containsKey(item)) {
              cartMap[item].quantity++;
              // total+=
            } else {
              cartMap[item] = ItemData(1, WidgetMarker.one, item);
            }
          });
        }
      },
      child: Row(
        children: <Widget>[
          Container(
            child: Padding(
              padding: const EdgeInsets.only(left: 12.0, right: 10),
              child: Text(
                'Add',
                style: h6,
              ),
            ),
          ),
          Container(
            child: Icon(
              Icons.add,
              color: primaryColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget getOneWidget(Item item) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        Container(
          width: 35,
          child: IconButton(
              iconSize: 20,
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
        Container(
          width: 15,
          child: Padding(
            padding: const EdgeInsets.only(),
            child: Text(
              cartMap[item].quantity.toString(),
              style: h6,
            ),
          ),
        ),
        Container(
          width: 30,
          child: IconButton(
              iconSize: 20,
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

class ItemData {
  int quantity = 0;
  WidgetMarker selectedWM;
  Item mItem;
  ItemData(this.quantity, this.selectedWM, this.mItem);
}

Future<List<Vendor>> _fetchMenu() async {
  final vendorListUrl = 'http://cf03fe8f0833.ngrok.io/api/user/dashboard/';
  final response = await get(
    vendorListUrl,
    headers: {
      'Authorization': "Token 57eff58c5cc493837b62b3b7f59ad19a6b633f4b",
      'username': 'user1',
      'password': 'user1pwd@123',
    },
  );
  print(response);
  if (response.statusCode == 200) {
    List jsonResponse = json.decode(response.body);
    return jsonResponse.map((job) => new Vendor.fromJson(job)).toList();
  } else {
    throw Exception('Failed to load jobs from API');
  }
}
