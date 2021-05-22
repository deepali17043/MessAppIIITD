import 'package:flutter/material.dart';
import 'package:flutter_easyloading/flutter_easyloading.dart';
import 'package:fryo/src/shared/colors.dart';
import 'package:fryo/src/shared/styles.dart';
import 'package:dropdown_date_picker/dropdown_date_picker.dart';
import 'package:flutter_dropdown/flutter_dropdown.dart';
import 'package:http/http.dart';
import '../shared/creds.dart';
import 'home_page.dart';

void sendAppIssue(String feedback) async {
  print(feedback);
  Response response = await post(
    url + 'api/accounts/app-feedback/',
    headers: {
      'Authorization': userToken,
      'feedback': feedback,
    },
  );

  print(response.body);
}

class AppIssuePage extends StatelessWidget {
  String issueFeedback = "";

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 2.0,
        centerTitle: true,
        title: Text(
          "App Feedback",
          style: h3,
        ),
        leading: IconButton(
          icon: Icon(Icons.arrow_back),
          color: Colors.black,
          onPressed: () {
            Navigator.pop(context);
          },
        ),
      ),
      body: Padding(
        padding: EdgeInsets.all(0.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            buildFeedbackForm(),
            Container(
              margin: EdgeInsets.all(5),
              decoration: BoxDecoration(
                color: Colors.greenAccent,
                borderRadius: BorderRadius.all(Radius.circular(10.0)),
              ),
              height: 60,
              alignment: Alignment.bottomCenter,
              // margin: EdgeInsets.only(top: 80),
              padding: EdgeInsets.all(5),
              width: double.infinity,
              child: FlatButton(
                  child: Text(
                    "Submit",
                    style: h8,
                  ),
                  onPressed: () {
                    if (issueFeedback != "") {
                      sendAppIssue(issueFeedback);
                      EasyLoading.showToast('Issue Raised');

                      Navigator.pop(context);
                    } else {
                      EasyLoading.showToast('Please fill all the fields');
                    }
                  }),
            )
          ],
        ),
      ),
    );
  }

  buildFeedbackForm() {
    return Container(
      height: 200,
      padding: EdgeInsets.all(10),
      child: Stack(
        children: [
          TextField(
            onChanged: (String p) {
              issueFeedback = p;
            },
            maxLines: 10,
            decoration: InputDecoration(
              hintText: "Please briefly describe the issue",
              hintStyle: TextStyle(
                fontSize: 13.0,
                color: Color(0xFFC5C5C5),
              ),
              border: OutlineInputBorder(
                borderSide: BorderSide(
                  color: Color(0xFFE5E5E5),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
