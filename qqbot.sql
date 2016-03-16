/*
Navicat MySQL Data Transfer

Source Server         : c-LAB
Source Server Version : 50547
Source Host           : localhost:3306
Source Database       : qqbot

Target Server Type    : MYSQL
Target Server Version : 50547
File Encoding         : 65001

Date: 2016-03-16 19:28:17
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for chat
-- ----------------------------
DROP TABLE IF EXISTS `chat`;
CREATE TABLE `chat` (
  `ask` varchar(255) NOT NULL,
  `answer` varchar(255) NOT NULL,
  `committer` bigint(20) NOT NULL,
  `deleted` int(2) NOT NULL DEFAULT '0',
  `gid` bigint(20) DEFAULT NULL,
  `time` datetime NOT NULL,
  PRIMARY KEY (`ask`,`answer`,`committer`),
  KEY `ask` (`ask`) USING BTREE,
  KEY `gid` (`gid`) USING BTREE,
  KEY `committer` (`committer`) USING BTREE,
  KEY `deleted` (`deleted`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for group
-- ----------------------------
DROP TABLE IF EXISTS `group`;
CREATE TABLE `group` (
  `gid` bigint(20) NOT NULL,
  `disabled` int(2) NOT NULL DEFAULT '0',
  `blocked` int(2) NOT NULL DEFAULT '0',
  PRIMARY KEY (`gid`),
  KEY `gid` (`gid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for group_relation
-- ----------------------------
DROP TABLE IF EXISTS `group_relation`;
CREATE TABLE `group_relation` (
  `uid` bigint(20) NOT NULL,
  `gid` bigint(20) NOT NULL,
  `coin` int(11) NOT NULL DEFAULT '0',
  `intimate` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`uid`,`gid`),
  KEY `uid_gid` (`uid`,`gid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `uid` bigint(20) NOT NULL,
  `coin` int(11) NOT NULL DEFAULT '0',
  `blocked` int(2) NOT NULL DEFAULT '0',
  PRIMARY KEY (`uid`),
  KEY `uid` (`uid`) USING BTREE,
  KEY `blocked` (`blocked`) USING BTREE,
  KEY `coin` (`coin`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
