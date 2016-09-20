/*
Navicat MySQL Data Transfer

Source Server         : 192.168.1.11
Source Server Version : 50710
Source Host           : 192.168.1.11:3366
Source Database       : scale

Target Server Type    : MYSQL
Target Server Version : 50710
File Encoding         : 65001

Date: 2016-09-20 16:57:14
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for app_scale_rule
-- ----------------------------
DROP TABLE IF EXISTS `app_scale_rule`;
CREATE TABLE `app_scale_rule` (
  `marathon_name` varchar(255) NOT NULL,
  `app_id` varchar(100) NOT NULL,
  `scale_type` varchar(255) NOT NULL,
  `scale_threshold` int(11) DEFAULT NULL,
  `per_auto_scale` int(11) DEFAULT NULL,
  `memory` int(11) DEFAULT NULL,
  `cpu` int(11) DEFAULT NULL,
  `thread` int(11) DEFAULT NULL,
  `ha_queue` int(11) DEFAULT NULL,
  `switch` int(11) DEFAULT NULL,
  `cold_time` int(10) DEFAULT NULL,
  `collect_period` int(10) DEFAULT NULL,
  `continue_period` int(10) DEFAULT NULL,
  PRIMARY KEY (`marathon_name`,`app_id`,`scale_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for quota_info
-- ----------------------------
DROP TABLE IF EXISTS `quota_info`;
CREATE TABLE `quota_info` (
  `marathon_name` varchar(255) NOT NULL,
  `app_id` varchar(255) NOT NULL,
  `rule_type` varchar(255) NOT NULL,
  `max_threshold` float(10,0) DEFAULT NULL,
  `min_threshold` float(10,0) DEFAULT NULL,
  PRIMARY KEY (`marathon_name`,`app_id`,`rule_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for scale_log
-- ----------------------------
DROP TABLE IF EXISTS `scale_log`;
CREATE TABLE `scale_log` (
  `id` int(255) NOT NULL AUTO_INCREMENT,
  `marathon_name` varchar(100) DEFAULT NULL,
  `app_id` varchar(100) DEFAULT NULL,
  `time` datetime(6) DEFAULT NULL,
  `count_status` varchar(255) DEFAULT NULL,
  `event` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
