import 'package:flutter/material.dart';
import 'package:flutter_easyloading/flutter_easyloading.dart';
import 'package:fryo/src/shared/colors.dart';
import 'package:fryo/src/shared/styles.dart';
import 'package:dropdown_date_picker/dropdown_date_picker.dart';
import 'package:flutter_dropdown/flutter_dropdown.dart';
import 'package:http/http.dart';
import '../shared/creds.dart';
import 'home_page.dart';

void sendIssue(String meal, String date, String feedback) async {
  print(meal + " " + date);
  Response response = await post(
    url + 'api/accounts/feedback/',
    headers: {
      'Authorization': userToken,
      'meal': meal,
      'date': date,
      'feedback': feedback,
    },
  );

  print(response.body);
}

class MessIssuePage extends StatelessWidget {
  static final now = DateTime.now();
  String issueDate = "";
  String issueMeal = "";
  String issueFeedback = "";
  final dropdownDatePicker = DropdownDatePicker(
    initialDate: ValidDate(year: now.year, month: now.month, day: now.day),
    firstDate: ValidDate(year: now.year, month: 1, day: 1),
    lastDate: ValidDate(year: now.year, month: now.month, day: now.day),
  );
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 2.0,
        centerTitle: true,
        title: Text(
          "Feedback",
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
            dropdownDatePicker,
            Center(
              child: DropDown(
                items: ["Breakfast", "Lunch", "Snacks", "Dinner"],
                hint: Text("Select Meal"),
                onChanged: (String m) {
                  issueMeal = m;
                },
              ),
            ),
            SizedBox(
              height: 20.0,
            ),
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
                    issueDate = dropdownDatePicker.getDate();
                    //   print(issueMeal + issueDate + issueFeedback);
                    if (issueFeedback != "" &&
                        dropdownDatePicker.year != null &&
                        dropdownDatePicker.month != null &&
                        dropdownDatePicker.day != null &&
                        issueMeal != '') {
                      sendIssue(issueMeal, issueDate, issueFeedback);
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
