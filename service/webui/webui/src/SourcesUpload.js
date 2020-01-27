import React from 'react';
import PropTypes from 'prop-types';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Tooltip from '@material-ui/core/Tooltip';
import IconButton from '@material-ui/core/IconButton';
import { withStyles } from '@material-ui/core/styles';
import SearchIcon from '@material-ui/icons/Search';
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

    directories[split.join("/")] = true;
  }

  if (directories.hasOwnProperty("")) {
    delete directories[""];
  }

  console.log(directories);

  for (var i in files) {
    files[i].id = Number(i);
  }

  setFilesInUploadDir(files);
}

function BasicTreeData() {
    const [filesInUploadDir, setFilesInUploadDir] = React.useState([]);
    const { data, error } = useSWR('/api/service/files', fetch)

    if (error) return <div>failed to load</div>
    if (!data) return <div>loading...</div>

    parseData(data, setFilesInUploadDir);

    return (
      <MaterialTable
        title="Files"
        data={filesInUploadDir}
        columns={[
          { title: 'Filename', field: 'filename', removable: false },
          { title: 'Size', field: 'size', type: 'numeric' },
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
  const { classes } = props;

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
        <BasicTreeData />
      </Paper>
    </React.Fragment>
  );
}

Content.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(Content);
