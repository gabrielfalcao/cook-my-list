import { StyleSheet } from "react-native";

export default StyleSheet.create({
  drawer: {
    paddingTop: 40,
  },
  topContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  card: {
    flex: 1,
    margin: 2,
  },
  container: {
    flex: 1,
    marginTop: 50,
    justifyContent: "flex-start",
    alignItems: "center",
    maxHeight: 80,
  },
  avatar: {
    margin: 8,
  },
  footerContainer: {
    flexDirection: "row",
    justifyContent: "flex-end",
  },
  footerControl: {
    marginHorizontal: 2,
  },
});
