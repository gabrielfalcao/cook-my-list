import React from "react";
import {
  Icon,
  MenuItem,
  OverflowMenu,
  TopNavigation,
  TopNavigationAction,
} from "@ui-kitten/components";

import {TopNavProps} from '../types'
const MenuIcon = (props) => <Icon {...props} name="menu-outline" />;

const SettingsIcon = (props) => <Icon {...props} name="settings-2-outline" />;

const LogoutIcon = (props) => <Icon {...props} name="log-out" />;

export const TopNav = ({ navigation }: TopNavProps): JSX.Element => {
  const [menuVisible, setMenuVisible] = React.useState(false);

  const toggleMenu = () => {
    navigation.openDrawer();
    //setMenuVisible(!menuVisible);
  };

  const renderMenuAction = () => (
    <TopNavigationAction icon={MenuIcon} onPress={toggleMenu} />
  );
  /*<TopNavigationAction icon={EditIcon}/> */

  // TODO: remove menu renderDrawerMenu as well as the menuVisible boolean state
  const renderDrawerMenu = () => (
    <React.Fragment>
      <OverflowMenu
        anchor={renderMenuAction}
        visible={menuVisible}
        onBackdropPress={toggleMenu}
      >
        <MenuItem accessoryLeft={SettingsIcon} title="Settings" />
        <MenuItem accessoryLeft={LogoutIcon} title="Logout" />
      </OverflowMenu>
    </React.Fragment>
  );

  const renderBackAction = () =>
    //<TopNavigationAction icon={BackIcon}/>
    null;

  return (
    <TopNavigation
      alignment="center"
      title="Cook My List"
      //subtitle='Search'
      accessoryLeft={renderDrawerMenu}
      //accessoryRight={renderRightActions}
    />
  );
};

export default TopNav;
