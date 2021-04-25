import React from "react";
import { RecipeDetailsProps, RecipeDetailsParams } from "cook-my-list/types";

import { SafeAreaView } from "react-native";
import {
  Divider,
  Layout,
  Text,
} from "@ui-kitten/components";
import TopNav from "../../widgets/topnav.component";

import styles from './styles'


export const RecipeDetailsScreen = ({ navigation }: RecipeDetailsProps): JSX.Element => {
  //const {recipeId}: RecipeDetailsParams = route.params
  return (
    <SafeAreaView style={{ flex: 1 }}>
      <TopNav navigation={navigation} />
      <Divider />
      <Layout style={styles.layout}>
        <Text category="h1">Recipe </Text>
      </Layout>
    </SafeAreaView>
  );
};

