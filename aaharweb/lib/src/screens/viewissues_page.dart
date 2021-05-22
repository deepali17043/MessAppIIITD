import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:fryo/src/screens/home_page.dart';
import 'package:fryo/src/shared/styles.dart';
import 'package:http/http.dart';
import 'package:page_transition/page_transition.dart';
import '../shared/creds.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:flutter_overlay_loader/flutter_overlay_loader.dart';

class ViewIssuePage extends StatefulWidget {
  ViewIssuePage({Key key}) : super(key: key);
  @override
  _ViewIssuePageState createState() => _ViewIssuePageState();
}

class _ViewIssuePageState extends State<ViewIssuePage> {
  var issueList = [];

  void getIssues() async {
    Loader.show(
      context,
      progressIndicator: CircularProgressIndicator(
        backgroundColor: Colors.white,
      ),
    );
    Response response = await post(
      url + 'api/accounts/view-feedback/',
      headers: {
        'Authorization': userToken,
      },
    );
    setState(() {
      issueList = jsonDecode(response.body);
    });
    Loader.hide();
  }

  @override
  void initState() {
    getIssues();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 2.0,
        centerTitle: true,
        title: Text(
          "Check Status",
          style: h3,
        ),
        leading: IconButton(
          icon: Icon(Icons.arrow_back),
          color: Colors.black,
          onPressed: () {
            Navigator.pop(
                context,
                PageTransition(
                    type: PageTransitionType.rightToLeft, child: HomePage()));
          },
        ),
      ),
      body: ListView(
        children: <Widget>[
          new ListView.builder(
              shrinkWrap: true,
              itemCount: issueList.length,
              itemBuilder: (BuildContext context, int index) {
                return _buildIssue(index);
              }),
        ],
      ),
    );
  }

  Widget _buildIssue(int index) {
    return Card(
      child: Container(
        padding: EdgeInsets.all(10),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Status: ' + issueList[index]['status'],
                  style: h4,
                ),
                Row(
                  children: [
                    Text(
                      issueList[index]['date'],
                      style: h6,
                    ),
                    SizedBox(
                      width: 10,
                    ),
                    Text(
                      issueList[index]['meal'],
                      style: h6,
                    ),
                  ],
                ),
              ],
            ),
            Row(
              children: [
                Expanded(
                  child: Container(
                    child: Text(
                      'Description: ' + issueList[index]['feedback'],
                      style: h5,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
