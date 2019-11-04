import React from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import { withStyles } from '@material-ui/core/styles';
import Divider from '@material-ui/core/Divider';
import Drawer from '@material-ui/core/Drawer';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import HomeIcon from '@material-ui/icons/Home';
import PeopleIcon from '@material-ui/icons/People';
import DnsRoundedIcon from '@material-ui/icons/DnsRounded';
import PermMediaOutlinedIcon from '@material-ui/icons/PhotoSizeSelectActual';
import PublicIcon from '@material-ui/icons/Public';
import SettingsEthernetIcon from '@material-ui/icons/SettingsEthernet';
import SettingsInputComponentIcon from '@material-ui/icons/SettingsInputComponent';
import TimerIcon from '@material-ui/icons/Timer';
import SettingsIcon from '@material-ui/icons/Settings';
import PhonelinkSetupIcon from '@material-ui/icons/PhonelinkSetup';
import BlurOnIcon from '@material-ui/icons/BlurOn';
import DesktopMacIcon from '@material-ui/icons/DesktopMac';
import LayersIcon from '@material-ui/icons/Layers';
import ListIcon from '@material-ui/icons/List';
import PlayArrowIcon from '@material-ui/icons/PlayArrow';
import FunctionsIcon from '@material-ui/icons/Functions';
import AllInclusiveIcon from '@material-ui/icons/AllInclusive';
import DeveloperBoardIcon from '@material-ui/icons/DeveloperBoard';
import AppsIcon from '@material-ui/icons/Apps';

const categories = [
  {
    id: 'Sources',
    children: [
      { id: 'Configure', icon: <DnsRoundedIcon />, active: true },
      { id: 'View', icon: <ListIcon /> },
    ],
  },
  {
    id: 'Models',
    children: [
      { id: 'Configure', icon: <DeveloperBoardIcon  /> },
      { id: 'Train', icon: <FunctionsIcon /> },
      { id: 'Predict', icon: <AllInclusiveIcon /> },
    ],
  },
  {
    id: 'Operations',
    children: [
      { id: 'View', icon: <AppsIcon /> },
      { id: 'Create', icon: <DesktopMacIcon /> },
      { id: 'Run', icon: <PlayArrowIcon /> },
    ],
  },
  {
    id: 'Dataflows',
    children: [
      { id: 'View', icon: <BlurOnIcon /> },
      { id: 'Create', icon: <SettingsEthernetIcon /> },
      { id: 'Deploy', icon: <PublicIcon /> },
    ],
  },
  {
    id: 'Settings',
    children: [
      { id: 'Backend', icon: <SettingsIcon /> },
    ],
  },
];

const styles = theme => ({
  categoryHeader: {
    paddingTop: theme.spacing(2),
    paddingBottom: theme.spacing(2),
  },
  categoryHeaderPrimary: {
    color: theme.palette.common.white,
  },
  item: {
    paddingTop: 1,
    paddingBottom: 1,
    color: 'rgba(255, 255, 255, 0.7)',
    '&:hover,&:focus': {
      backgroundColor: 'rgba(255, 255, 255, 0.08)',
    },
  },
  itemCategory: {
    backgroundColor: '#232f3e',
    boxShadow: '0 -1px 0 #404854 inset',
    paddingTop: theme.spacing(2),
    paddingBottom: theme.spacing(2),
  },
  firebase: {
    fontSize: 24,
    color: theme.palette.common.white,
  },
  itemActiveItem: {
    color: '#4fc3f7',
  },
  itemPrimary: {
    fontSize: 'inherit',
  },
  itemIcon: {
    minWidth: 'auto',
    marginRight: theme.spacing(2),
  },
  divider: {
    marginTop: theme.spacing(2),
  },
});

function Navigator(props) {
  const { classes, ...other } = props;

  return (
    <Drawer variant="permanent" {...other}>
      <List disablePadding>
        <ListItem className={clsx(classes.firebase, classes.item, classes.itemCategory)}>
          dataflow.ml
        </ListItem>
        {categories.map(({ id, children }) => (
          <React.Fragment key={id}>
            <ListItem className={classes.categoryHeader}>
              <ListItemText
                classes={{
                  primary: classes.categoryHeaderPrimary,
                }}
              >
                {id}
              </ListItemText>
            </ListItem>
            {children.map(({ id: childId, icon, active }) => (
              <ListItem
                key={childId}
                button
                className={clsx(classes.item, active && classes.itemActiveItem)}
              >
                <ListItemIcon className={classes.itemIcon}>{icon}</ListItemIcon>
                <ListItemText
                  classes={{
                    primary: classes.itemPrimary,
                  }}
                >
                  {childId}
                </ListItemText>
              </ListItem>
            ))}

            <Divider className={classes.divider} />
          </React.Fragment>
        ))}
      </List>
    </Drawer>
  );
}

Navigator.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(Navigator);
