Name:		mxparser
Version:	1.2.3
Release:	1
Summary:	Minimal XML pull parser
Group:		Development/Java
License:	Indiana University Extreme! Lab Software License
URL:		https://github.com/x-stream/mxparser
Source0:	https://github.com/x-stream/mxparser/archive/refs/tags/v-%{version}.tar.gz#/mxparser-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	mvn(xmlpull:xmlpull)

%description
MXParser is the XML pull parser XStream uses by default. It is a
fork of the xpp3 minimal parser and implements the XmlPull API.
1.2.3 fixes the entity parser cache. Gradle's Groovy compiler
reaches it when XStream is constructed without a StaxDriver.

%prep
%autosetup -n mxparser-v-%{version}

%build
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH=$JAVA_HOME/bin:$PATH
mkdir -p classes/META-INF/services
javac --release 8 -encoding UTF-8 -Xlint:-options \
	-cp %{_javadir}/xmlpull.jar \
	-d classes \
	src/main/java/io/github/xstream/mxparser/MXParser.java
cp src/main/resources/META-INF/services/* classes/META-INF/services/
jar cf %{name}.jar -C classes .
cat > %{name}.pom <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>io.github.x-stream</groupId>
  <artifactId>mxparser</artifactId>
  <version>%{version}</version>
  <name>MXParser</name>
  <description>Minimal XML pull parser implementing the XmlPull API.</description>
  <url>https://github.com/x-stream/mxparser</url>
  <licenses>
    <license>
      <name>Indiana University Extreme! Lab Software License, Version 1.2</name>
      <url>https://raw.githubusercontent.com/x-stream/mxparser/v-%{version}/LICENSE.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>xmlpull</groupId>
      <artifactId>xmlpull</artifactId>
      <version>1.1.3.4c</version>
    </dependency>
  </dependencies>
</project>
EOF

%check
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH=$JAVA_HOME/bin:$PATH
mkdir -p check
cat > check/Smoke.java <<'END'
import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserFactory;
public class Smoke {
	public static void main(String[] args) throws Exception {
		XmlPullParserFactory factory = XmlPullParserFactory.newInstance();
		XmlPullParser parser = factory.newPullParser();
		parser.setInput(new java.io.StringReader("<a>gradle</a>"));
		String text = null;
		for (int ev = parser.next(); ev != XmlPullParser.END_DOCUMENT; ev = parser.next()) {
			if (ev == XmlPullParser.TEXT) {
				text = parser.getText();
			}
		}
		if (!"gradle".equals(text)) {
			throw new AssertionError(text);
		}
		if (!parser.getClass().getName().equals("io.github.xstream.mxparser.MXParser")) {
			throw new AssertionError(parser.getClass().getName());
		}
		System.out.println("ok");
	}
}
END
javac --release 8 -encoding UTF-8 -Xlint:-options \
	-cp %{name}.jar:%{_javadir}/xmlpull.jar \
	-d check check/Smoke.java
test "$(java -cp check:%{name}.jar:%{_javadir}/xmlpull.jar Smoke)" = ok

%install
sysjar install --buildroot %{buildroot} \
	--artifact %{name}.pom:%{name}.jar \
	--file-name %{name} \
	--filelist .mfiles

%files -f .mfiles
%doc LICENSE.txt README.md
