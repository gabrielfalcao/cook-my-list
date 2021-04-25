import React from "react";
import { StyleSheet } from "react-native";
import { RecipeDetailsProps, RecipeDetailsParams } from "cook-my-list/types";

import { SafeAreaView } from "react-native";
import {
  Divider,
  Layout,
  Text,
} from "@ui-kitten/components";
import TopNav from "cook-my-list/widgets/topnav.component";



export const RecipeDetailsScreen = ({ navigation, route }: RecipeDetailsProps): JSX.Element => {
  const {recipeId}: RecipeDetailsParams = route.params
  return (
    <SafeAreaView style={{ flex: 1 }}>
      <TopNav navigation={navigation} />
      <Divider />
      <Layout style={styles.layout}>
        <Text category="h1">Recipe {recipeId}</Text>
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
