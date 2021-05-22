import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:fryo/src/shared/api_consts.dart';
import 'package:page_transition/page_transition.dart';
import '../shared/styles.dart';
import '../shared/colors.dart';
import 'package:http/http.dart';
import '../screens/base_page.dart';
import '../shared/vendor.dart';
import 'menu_page.dart';

class VendorPage extends StatefulWidget {
  final String pageTitle;
  final bool back;
  VendorPage({Key key, this.pageTitle, this.back}) : super(key: key);

  @override
  _VendorPageState createState() => _VendorPageState(back);
}

void getVendorList() {}

class _VendorPageState extends State<VendorPage> {
  bool back;

  List<String> venList = ['Canteen', 'Kodechef'];
  _VendorPageState(this.back);
  @override
  Widget build(BuildContext context) {
    _fetchVendors('v');
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
        title:
            Text('Choose your outlet', style: h3, textAlign: TextAlign.center),
      ),
      body: Column(
        children: <Widget>[
          new ListView.builder(
              shrinkWrap: true,
              itemCount: venList.length,
              itemBuilder: (BuildContext context, int index) {
                return _buildVendorName(venList[index], true);
              }),
        ],
      ),
    );
  }

  Widget _buildVendorName(String venName, bool active) {
    return GestureDetector(
      onTap: () {},
      child: Container(
        child: Column(
          children: <Widget>[
            Padding(
                padding: EdgeInsets.only(left: 10.0, right: 10.0, top: 10.0),
                child: InkWell(
                    onTap: () {
                      setState(() {
                        Navigator.push(
                            context,
                            PageTransition(
                                type: PageTransitionType.rightToLeft,
                                child: BasePage(
                                  pageTitle: venName,
                                )));
                      });
                    },
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: <Widget>[
                        Container(
                            child: Row(children: <Widget>[
                          Column(
                              //   crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(venName,
                                    style: TextStyle(
                                      fontFamily: 'Montserrat',
                                      fontSize: 20.0,
                                    )),
                              ])
                        ])),
                        IconButton(
                            icon: Icon(
                              Icons.arrow_forward,
                              color: primaryColor,
                            ),
                            color: darkText,
                            onPressed: () {})
                      ],
                    ))),
            SizedBox(
              child: Divider(
                color: Colors.teal,
              ),
              height: 10,
            )
          ],
        ),
      ),
    );
  }
}

Future<List<Vendor>> _fetchVendors(String token) async {
  final vendorListUrl = api_url + '/api/accounts/dashboard/';
  final response = await get(
    vendorListUrl,
    headers: {
      'Authorization': token,
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
