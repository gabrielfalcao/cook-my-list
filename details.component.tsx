import React from "react";
import { StyleSheet } from "react-native";

import { SafeAreaView } from "react-native";
import {
  Divider,
  Icon,
  Layout,
  Text,
  TopNavigationAction,
} from "@ui-kitten/components";
import TopNav from "./topnav.component";

const BackIcon = (props) => <Icon {...props} name="" />;

export const DetailsScreen = ({ navigation }) => {
  return (
    <SafeAreaView style={{ flex: 1 }}>
      <TopNav navigation={navigation} />
      <Divider />
      <Layout style={styles.layout}>
        <Text category="h1">Recipe 1</Text>
      </Layout>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  layout: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    flexDirection: "row",
    flexWrap: "wrap",
  },
});
