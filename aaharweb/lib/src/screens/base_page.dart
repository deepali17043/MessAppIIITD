import 'dart:convert';
import 'package:flutter/material.dart';
import '../shared/styles.dart';
import '../shared/colors.dart';
import 'package:http/http.dart';
import '../shared/items.dart';
import '../screens/menu_page.dart';
import '../shared/vendor.dart';
import 'cart_page.dart';

Vendor selectedVendor;

class Destination {
  const Destination(this.title, this.icon, this.color, this.curPage);
  final String title;
  final IconData icon;
  final Color color;
  final Widget curPage;
}

List<Destination> allDestinations = <Destination>[
  Destination(
      "Menu", Icons.home, primaryColor, MenuPage(vendorName: selectedVendor)),
  Destination('Cart', Icons.shopping_basket, primaryColor, CartPage()),
  // Destination('Account', Icons.account_circle, primaryColor, CartPage()),
];

class BasePage extends StatefulWidget {
  final String pageTitle;

  BasePage({Key key, this.pageTitle}) : super(key: key);

  @override
  _BasePageState createState() => _BasePageState(pageTitle);
}

class _BasePageState extends State<BasePage> {
  int _currentIndex = 0;
  String pageTitle;
  _BasePageState(this.pageTitle);
  @override
  Widget build(BuildContext context) {
    selectedVendor = Vendor(name: pageTitle);
    return Scaffold(
      body: SafeArea(
        top: false,
        child: allDestinations[_currentIndex].curPage,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (int index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: allDestinations.map((Destination destination) {
          return BottomNavigationBarItem(
              icon: Icon(destination.icon),
              backgroundColor: destination.color,
              title: Text(destination.title));
        }).toList(),
      ),
    );
  }
}
