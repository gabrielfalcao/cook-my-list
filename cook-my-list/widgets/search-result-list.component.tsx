import React from "react";
import { StyleSheet, ListRenderItemInfo } from "react-native";

import { Recipe, WidgetNavigationProp} from "../types";
import { recipes } from "../ingredients.constants";
import RecipeCard from "./recipe-card.component";
import { List, Text } from "@ui-kitten/components";

type Props = {
  navigation: WidgetNavigationProp;
  chosenIngredientNames: Array<string>;
}

export const SearchResultList = ({
  chosenIngredientNames,
  navigation,
  ...props
}: Props): JSX.Element => {
  const renderHorizontalTrainingItem = (
    info: ListRenderItemInfo<Recipe>
  ): React.ReactElement => (
    <RecipeCard
      style={styles.horizontalItem}
      recipe={info.item}
      onPress={() => {
        console.log(`RecipeCard onPress`, info);
        navigation.navigate("Details");
      }}
    />
  );
  return (
    <React.Fragment>
      <Text style={styles.headerTitle} appearance="hint">
        Encontramos 3 receitas com:
      </Text>
      <Text style={styles.headerTitle} appearance="hint">
        {chosenIngredientNames.join(", ")}
      </Text>
      <List
        contentContainerStyle={styles.horizontalList}
        horizontal={true}
        showsHorizontalScrollIndicator={false}
        data={recipes}
        renderItem={renderHorizontalTrainingItem}
      />
    </React.Fragment>
  );
};

const styles = StyleSheet.create({
  questionTitle: {
    paddingTop: 15,
    paddingBottom: 15,
    fontSize: 16,
    textAlign: "center",
    width: "100%",

  },
  container: {
    maxHeight: "100%",
    marginHorizontal: 20,
    marginTop: 5,
  },
  contentContainer: {
    minWidth: "100%",
  },
  list: {
    paddingVertical: 24,
  },
  headerTitle: {
    marginHorizontal: 16,
    textAlign: "center",
    width: "100%",
    fontSize: 15,
    padding: 5,
    textAlignVertical: "center",
  },
  horizontalList: {
    marginVertical: 16,
    paddingHorizontal: 8,
  },
  verticalItem: {
    marginVertical: 8,
    marginHorizontal: 16,
  },
  horizontalItem: {
    width: 256,
    marginHorizontal: 8,
  },
});
export default SearchResultList;
