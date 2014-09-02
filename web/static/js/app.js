/** @jsx React.DOM */
'use strict';

var apiUrl = 'http://192.168.0.100/api/newdeveloper';

function hsbToRgb(h, s, l) {
  function hue2rgb(p, q, t) {
    if(t < 0) t += 1;
    if(t > 1) t -= 1;
    if(t < 1/6) return p + (q - p) * 6 * t;
    if(t < 1/2) return q;
    if(t < 2/3) return p + (q - p) * (2/3 - t) * 6;
    return p;
  }

  var r, g, b;

  if (s == 0) {
    r = g = b = l; // achromatic
  } else {
    var q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    var p = 2 * l - q;
    r = hue2rgb(p, q, h + 1/3);
    g = hue2rgb(p, q, h);
    b = hue2rgb(p, q, h - 1/3);
  }

  return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
};

var App = React.createClass({
  getInitialState: function() {
    return {
      lights: {}
    };
  },

  componentWillMount: function() {
    var self = this;

    $.getJSON(apiUrl + '/lights', function(data) {
      self.setState({
        lights: data
      });
    });
  },

  render: function() {
    var kitchen, living1, living2, bathroom, brian, wang;

    if (!_.isEmpty(this.state.lights)) {
      kitchen = <Light id="2" data={this.state.lights['2']} />;
      living1 = <Light id="1" data={this.state.lights['1']} />;
      living2 = <Light id="3" data={this.state.lights['3']} />;
      bathroom = <Light id="4" data={this.state.lights['4']} />;
      brian = <Light id="5" data={this.state.lights['5']} />;
      wang = <Light id="6" data={this.state.lights['6']} />;
    }

    return (
      <div>
        <div>
          <h2>Kitchen</h2>
          {kitchen}
        </div>
        <div>
          <h2>Living</h2>
          {living1}
          {living2}
        </div>
        <div>
          <h2>Bathroom</h2>
          {bathroom}
        </div>
        <div>
          <h2>Wang</h2>
          {wang}
        </div>
        <div>
          <h2>Brian</h2>
          {brian}
        </div>
      </div>
    );
  }
});

var Light = React.createClass({
  mixins: [React.addons.LinkedStateMixin],

  getInitialState: function() {
    return {};
  },

  componentDidMount: function() {
    this.componentWillReceiveProps(this.props);
  },

  componentWillReceiveProps: function(nextProps) {
    this.setState({
      name: nextProps.data.name,
      on: nextProps.data.state.on,
      hue: nextProps.data.state.hue,
      sat: nextProps.data.state.sat,
      bri: nextProps.data.state.bri,
    });
  },

  handleToggleOnOff: function() {
    var self = this;
    $.ajax({
      url: apiUrl + '/lights/' + this.props.id + '/state',
      type: 'PUT',
      data: JSON.stringify({on: !this.state.on}),
      success: function(data) {
        self.setState({
          on: !self.state.on
        });
      }
    });
  },

  handleChangeValues: function(e) {
    var self = this;
    if (e.keyCode == 13) {
      $.ajax({
        url: apiUrl + '/lights/' + this.props.id + '/state',
        type: 'PUT',
        data: JSON.stringify({
          hue: parseInt(this.state.hue),
          sat: parseInt(this.state.sat),
          bri: parseInt(this.state.bri)
        }),
        success: function(data) {
        }
      });
    }
  },

  render: function() {
    return (
      <div style={{background: 'rgb(' + hsbToRgb(this.state.hue/65535, 1, 1-this.state.sat/254/2) + ')'}}>
        <form className="form-horizontal" role="form">
          <div className="form-group">
            <label className="col-sm-2 control-label"></label>
            <div className="col-sm-10">
              <button type="button" className="btn btn-default" onClick={this.handleToggleOnOff}>{this.state.on ? 'On' : 'Off'}</button>
            </div>
          </div>
          <div className="form-group">
            <label className="col-sm-2 control-label">Name</label>
            <div className="col-sm-10">
              <input type="text" className="form-control" valueLink={this.linkState('name')} />
            </div>
          </div>
          <div className="form-group">
            <label className="col-sm-2 control-label">Hue</label>
            <div className="col-sm-10">
              <input type="text" className="form-control" valueLink={this.linkState('hue')} onKeyUp={this.handleChangeValues} />
            </div>
          </div>
          <div className="form-group">
            <label className="col-sm-2 control-label">Saturation</label>
            <div className="col-sm-10">
              <input type="text" className="form-control" valueLink={this.linkState('sat')} onKeyUp={this.handleChangeValues} />
            </div>
          </div>
          <div className="form-group">
            <label className="col-sm-2 control-label">Brightness</label>
            <div className="col-sm-10">
              <input type="text" className="form-control" valueLink={this.linkState('bri')} onKeyUp={this.handleChangeValues} />
            </div>
          </div>
        </form>
      </div>
    );
  }
});

React.renderComponent(<App />, document.getElementById('body-container'));
