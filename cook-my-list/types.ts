import { RouteProp } from '@react-navigation/native';
import { DrawerNavigationProp } from "@react-navigation/drawer";

export type RecipeDetailsParams = { recipeId : string}
export type RootStackParamList = {
    Home: undefined;
    Logout: undefined;
    RecipeDetails: RecipeDetailsParams;
    Profile: { userId: string };
    Feed: { sort: 'latest' | 'top' } | undefined;
};

export interface Ingredient {
    name: string,
    imageName: string,
}

export interface Recipe {
    title: string,
    imageName: string,
    tags: RecipeTag[]
}

export interface RecipeTag {
    name: string,
    iconName: string,
}


export type HomeScreenRouteProp = RouteProp<RootStackParamList, 'Home'>;
export type HomeScreenNavigationProp = DrawerNavigationProp<
  RootStackParamList,
  'Home'
>;
export type HomeScreenProps = {
  route: HomeScreenRouteProp,
  navigation: HomeScreenNavigationProp
}

export type RecipeDetailsScreenRouteProp = RouteProp<RootStackParamList, 'Home'>;
export type RecipeDetailsScreenNavigationProp = DrawerNavigationProp<
  RootStackParamList,
  'RecipeDetails'
>;
export type RecipeDetailsProps = {
  route: RecipeDetailsScreenRouteProp,
  navigation: RecipeDetailsScreenNavigationProp
}


export type LogoutScreenRouteProp = RouteProp<RootStackParamList, 'Logout'>;
export type LogoutScreenNavigationProp = DrawerNavigationProp<
  RootStackParamList,
  'Logout'
>;
export type LogoutScreenProps = {
  route: LogoutScreenRouteProp,
  navigation: LogoutScreenNavigationProp
}


export type WidgetNavigationProp = HomeScreenNavigationProp | RecipeDetailsScreenNavigationProp | LogoutScreenNavigationProp