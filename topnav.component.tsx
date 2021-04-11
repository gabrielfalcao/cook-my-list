import React from 'react';
import { Icon, Layout, MenuItem, OverflowMenu, TopNavigation, TopNavigationAction } from '@ui-kitten/components';
import { StyleSheet } from 'react-native';

const BackIcon = (props) => (
  <Icon {...props} name='arrow-back'/>
);

const EditIcon = (props) => (
  <Icon {...props} name='edit'/>
);

const MenuIcon = (props) => (
  <Icon {...props} name='more-vertical'/>
);

const SettingsIcon = (props) => (
  <Icon {...props} name='settings-2-outline'/>
);

const LogoutIcon = (props) => (
  <Icon {...props} name='log-out'/>
);

export const TopNavigationAccessoriesShowcase = ({}) => {

  const [menuVisible, setMenuVisible] = React.useState(false);

  const toggleMenu = () => {
    setMenuVisible(!menuVisible);
  };

  const renderMenuAction = () => (
    <TopNavigationAction icon={MenuIcon} onPress={toggleMenu}/>
  );
      /*<TopNavigationAction icon={EditIcon}/> */

  const renderRightActions = () => (
    <React.Fragment>
      <OverflowMenu
        anchor={renderMenuAction}
        visible={menuVisible}
        onBackdropPress={toggleMenu}>
        <MenuItem accessoryLeft={SettingsIcon} title='Settings'/>
        <MenuItem accessoryLeft={LogoutIcon} title='Logout'/>
      </OverflowMenu>
    </React.Fragment>
  );

  const renderBackAction = () => (
    //<TopNavigationAction icon={BackIcon}/>
    null
  );

  return (
      <TopNavigation
        alignment='center'
        title='Cook My List'
        //subtitle='Search'
        accessoryLeft={renderBackAction}
        accessoryRight={renderRightActions}
      />
  );
};

export default TopNavigationAccessoriesShowcase;