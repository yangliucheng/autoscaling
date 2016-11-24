package db

import (
	"Stardigi-Policy/utils"
	"database/sql"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
)

var (
	DBsqler = make(map[string]Sqler)
)

type DBclient struct {
	object interface{}
	Db     *sql.DB
	StrSql string
}

func SetDBsqler(name string, sqler Sqler) {

	DBsqler[name] = sqler
}

func GetDBsqker(name string) Sqler {

	return DBsqler[name]
}

func NewDBClient(dbType, dataSourceName string) *DBclient {

	db, err := sql.Open(dbType, dataSourceName)
	if err != nil {
		fmt.Println("数据库初始化失败，错误信息：", err)
	}

	dbClient := &DBclient{
		Db: db,
	}
	SetDBsqler(dbType, dbClient)
	return dbClient
}

func (dbClient *DBclient) Insert(object interface{}) {

	name := utils.NameParaseWithReflect(object)
	table := utils.StringParaseWith_(name)
	stat, value := utils.ParaseInterface(object)

	con := utils.StringJoin("INSERT INTO ", table, " SET ", stat)
	db := dbClient.Db
	stmt, err := db.Prepare(con)
	if err != nil {
		fmt.Println("插入数据看失败", err)
	}
	_, err = stmt.Exec(value...)
	if err != nil {
		fmt.Println("插入数据看失败", err)
	}
}

func (dbClient *DBclient) QueryTable(object interface{}) QuerySet {

	// dbClient.StrChan = make(chan string, 1)

	name := utils.NameParaseWithReflect(object)
	table := utils.StringParaseWith_(name)

	str := utils.StringJoin("SELECT * from ", table)

	dbClient.StrSql = str
	dbClient.object = object
	starQuerySet := NewStarQuerySet(dbClient)
	return starQuerySet
}
