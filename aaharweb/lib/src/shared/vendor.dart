class Vendor {
  final String name;

  Vendor({this.name});

  factory Vendor.fromJson(Map<String, dynamic> json) {
    return Vendor(
      name: json['name'],
    );
  }
}
