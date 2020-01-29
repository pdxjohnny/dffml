import React from 'react';
import PropTypes from 'prop-types';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Tooltip from '@material-ui/core/Tooltip';
import IconButton from '@material-ui/core/IconButton';
import { withStyles } from '@material-ui/core/styles';
import RefreshIcon from '@material-ui/icons/Refresh';
import MaterialTable from 'material-table';
import {DropzoneArea} from 'material-ui-dropzone';
import useSWR from 'swr';

const styles = theme => ({
  paper: {
    maxWidth: 936,
    margin: 'auto',
    overflow: 'hidden',
  },
  searchBar: {
    borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
  },
  searchInput: {
    fontSize: theme.typography.fontSize,
  },
  block: {
    display: 'block',
  },
  addUser: {
    marginRight: theme.spacing(1),
  },
  contentWrapper: {
    margin: '40px 16px',
  },
});

async function parseData(data, setFilesInUploadDir) {
  if (data.bodyUsed) {
    return
  }

  var files = await data.json();

  var directories = {};

  for (var i in files) {
    files[i].id = Number(i);

    var split = files[i].filename.split("/");

    split.pop();

    directories[split.join("/") + "/"] = true;
  }

  if (directories.hasOwnProperty("/")) {
    delete directories["/"];
  }

  for (i = 0; i < Object.keys(directories).length; i++) {
    directories[Object.keys(directories)[i]] = files.length + i;
  }

  for (i in directories) {
    split = i.split("/");

    split.pop();

    var directory = {
      id: directories[i],
      filename: split[split.length - 1] + "/",
    }
    split.pop();

    var joined = split.join("/") + "/";

    if (directories.hasOwnProperty(joined)) {
      directory.parentId = directories[joined];
    }

    files.push(directory);
  }

  for (i in files) {
    if (files[i].filename.endsWith("/")) {
      continue;
    }

    split = files[i].filename.split("/");

    files[i].filename = split[split.length - 1];

    split.pop();

    joined = split.join("/") + "/";

    if (directories.hasOwnProperty(joined)) {
      files[i].parentId = directories[joined];
    }
  }

  setFilesInUploadDir(files);
}

function BasicTreeData(props) {
    const [filesInUploadDir, setFilesInUploadDir] = React.useState([]);
    console.log("Files and Uploads backend:", props.backend);
    // TODO Change this URL
    var { data, error } = useSWR(props.backend.url + '/service/files', fetch)

    var localization = {};

    // TODO, handle error
    if (error) {
      data = []
      localization.body = {
        emptyDataSourceMessage: "Error loading files",
      };
    } else if (!data) {
      data = []
      localization.body = {
        emptyDataSourceMessage: "No files",
      };
    } else {
      parseData(data, setFilesInUploadDir);
    }

    return (
      <MaterialTable
        title="Files"
        localization={localization}
        data={filesInUploadDir}
        columns={[
          { title: 'Filename', field: 'filename', removable: false },
          { title: 'Size (MB)', field: 'size', type: 'numeric' },
        ]}
        parentChildData={(row, rows) => rows.find(a => a.id === row.parentId)}
        options={{
          selection: true,
        }}
      />
    )
}

class DropzoneAreaExample extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      files: []
    };
  }
  handleChange(files){
    this.setState({
      files: files
    });
  }
  render(){
    return (
      <DropzoneArea
        dropzoneText="Drag and drop a file here or click"
        showFileNames={true}
        acceptedFiles={[]}
        onChange={this.handleChange.bind(this)}
      />
    )
  }
}

function Content(props) {
  const { classes, backend } = props;

  return (
    <React.Fragment>
      <Paper className={classes.paper}>
        <DropzoneAreaExample />
        <AppBar className={classes.searchBar} position="static" color="default" elevation={0}>
          <Toolbar>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs>
                <TextField
                  fullWidth
                  placeholder="Path to place file at"
                  InputProps={{
                    disableUnderline: true,
                    className: classes.searchInput,
                  }}
                />
              </Grid>
              <Grid item>
                <Button disabled={true} variant="contained" color="primary" className={classes.addUser}>
                  Upload File
                </Button>
                <Tooltip title="Reload">
                  <IconButton>
                    <RefreshIcon className={classes.block} color="inherit" />
                  </IconButton>
                </Tooltip>
              </Grid>
            </Grid>
          </Toolbar>
        </AppBar>
      </Paper>
      <br />
      <Paper className={classes.paper}>
        <BasicTreeData backend={backend} />
      </Paper>
    </React.Fragment>
  );
}

Content.propTypes = {
  classes: PropTypes.object.isRequired,
  backend: PropTypes.object.isRequired,
};

export default withStyles(styles)(Content);
