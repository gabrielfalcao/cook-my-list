const { getDefaultConfig } = require("@expo/metro-config");
const path = require("path");

module.exports = (async () => {
  const {
    resolver: { sourceExts, assetExts }
  } = await getDefaultConfig(__dirname);
  return {
    transformer: {
      babelTransformerPath: require.resolve("react-native-svg-transformer")
    },
    resolver: {
      assetExts: assetExts.filter(ext => ext !== "svg"),
      sourceExts: [...sourceExts, "svg"]
    },
    resolveRequest: (context, realModuleName, platform, moduleName) => {
      
      switch(moduleName) {
        case "cook-my-list":
          return {
            filePath: path.resolve(__dirname, "cook-my-list"),
            type: 'sourceFile',
          };
        default:
          break;
      }
    }
  };
})();