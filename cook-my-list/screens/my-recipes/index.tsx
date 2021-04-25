import React from "react";
import { StyleSheet } from "react-native";

import { SafeAreaView } from "react-native";
import { Divider, Layout, Text } from "@ui-kitten/components";
import { MyRecipesScreenProps } from "../../types";

import TopNav from "../../widgets/topnav.component";

export const MyRecipesScreen = ({ navigation }: MyRecipesScreenProps): JSX.Element => {
  return (
    <SafeAreaView style={{ flex: 1 }}>
      <TopNav navigation={navigation} />

      <Divider />
      <Layout style={styles.layout}>
        <Text style={styles.title} category="h4">
          Minhas Receitas
        </Text>
      </Layout>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  button: {
    margin: 10,
  },
  title: { marginTop: 100 },
  layout: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    flexDirection: "row",
    flexWrap: "wrap",
  },
});
