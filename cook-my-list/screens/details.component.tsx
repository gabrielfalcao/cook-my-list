import React from "react";
import { StyleSheet } from "react-native";
import { RouteProp } from '@react-navigation/native';
import { DrawerNavigationProp } from "@react-navigation/drawer";
import { RootStackParamList, RecipeDetailsParams } from "cook-my-list/types";

import { SafeAreaView } from "react-native";
import {
  Divider,
  Layout,
  Text,
} from "@ui-kitten/components";
import TopNav from "cook-my-list/widgets/topnav.component";

type RecipeDetailsScreenRouteProp = RouteProp<RootStackParamList, 'Home'>;
type RecipeDetailsScreenNavigationProp = DrawerNavigationProp<
  RootStackParamList,
  'RecipeDetails'
>;
type Props = {
  route: RecipeDetailsScreenRouteProp,
  navigation: RecipeDetailsScreenNavigationProp
}

export const RecipeDetailsScreen = ({ navigation, route }: Props): JSX.Element => {
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
