import React from "react";
import { StyleSheet } from "react-native";

import { TouchableWithoutFeedback } from "react-native";
import {
  Autocomplete,
  AutocompleteItem,
  Icon,
  Avatar,
} from "@ui-kitten/components";
import { ingredients } from "./ingredients.constants";
import foodImages from "./food-images";

const filter = (item, query) =>
  item.name.toLowerCase().includes(query.toLowerCase());

export const IngredientSearch = ({
  addIngredient,
  chosenIngredientNames,
  ...props
}) => {
  const [value, setValue] = React.useState(null);
  const [data, setData] = React.useState(ingredients);

  const onSelect = (index) => {
    setValue("");

    addIngredient(data[index]);
  };

  const onChangeText = (query) => {
    setData(ingredients.filter((item) => filter(item, query)));
  };

  const clearInput = () => {
    setValue("");
    setData(ingredients);
  };

  const renderOption = (item, index) => {
    const FoodImage = ({ ...props }) => (
      <Avatar
        {...props}
        style={[props.style, { tintColor: null }]}
        source={foodImages[item.imageName]}
      />
    );
    return (
      <AutocompleteItem
        key={index}
        title={item.name}
        accessoryLeft={FoodImage}
      />
    );
  };

  const renderCloseIcon = (props) => (
    <TouchableWithoutFeedback onPress={clearInput}>
      <Icon {...props} name="search-outline" />
    </TouchableWithoutFeedback>
  );

  return (
    <Autocomplete
      placeholder="Adicionar Ingrediente"
      value={value}
      accessoryRight={renderCloseIcon}
      onChangeText={onChangeText}
      size="large"
      onSelect={onSelect}
      {...props}
    >
      {data.map(renderOption)}
    </Autocomplete>
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
});
export default IngredientSearch;
